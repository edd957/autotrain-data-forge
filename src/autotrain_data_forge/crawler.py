from __future__ import annotations

import time
from collections import deque
from hashlib import sha256
from pathlib import Path
from re import IGNORECASE, error, search
from urllib.parse import unquote, urldefrag, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from autotrain_data_forge.config import get_settings
from autotrain_data_forge.extractors import extract_page
from autotrain_data_forge.io import append_jsonl
from autotrain_data_forge.schemas import CrawlResult, HarvestJob
from autotrain_data_forge.security import has_blocking_findings, review_job


class SafeCrawler:
    def __init__(self, job: HarvestJob, workspace: Path | None = None) -> None:
        self.job = job
        self.workspace = workspace or Path.cwd()
        self.output_dir = self.workspace / job.output_dir
        self.settings = get_settings()
        self.robots_cache: dict[str, RobotFileParser] = {}

    def crawl(self, dry_run: bool = False) -> CrawlResult:
        findings = review_job(self.job, self.workspace)
        if has_blocking_findings(findings):
            blocked_warnings = [f"{finding.code}: {finding.message}" for finding in findings]
            return CrawlResult(
                pages_seen=0,
                pages_saved=0,
                images_saved=0,
                output_dir=self.output_dir,
                warnings=blocked_warnings,
            )
        if dry_run:
            return CrawlResult(
                pages_seen=0,
                pages_saved=0,
                images_saved=0,
                output_dir=self.output_dir,
                warnings=["dry_run: no network requests made"],
            )

        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in self.job.seeds)
        seen: set[str] = set()
        pages_saved = 0
        images_saved = 0
        warnings: list[str] = []

        with httpx.Client(
            timeout=self.settings.request_timeout_seconds,
            headers={"User-Agent": self.settings.default_user_agent},
            follow_redirects=True,
        ) as client:
            while queue and pages_saved < self.job.max_pages:
                url, depth = queue.popleft()
                normalized = urldefrag(url).url
                if normalized in seen or not self._is_allowed(normalized):
                    continue
                seen.add(normalized)
                if not self._robots_allowed(normalized):
                    warnings.append(f"blocked_by_robots: {normalized}")
                    continue
                try:
                    response = client.get(normalized)
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    warnings.append(f"request_failed: {normalized}: {exc}")
                    continue
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    continue
                extracted = extract_page(response.text, normalized)
                if not self._matches_filters(normalized, extracted.title, extracted.text):
                    continue
                self._save_page(normalized, extracted.title, extracted.text)
                pages_saved += 1
                if self.job.include_images:
                    images_saved += self._save_images(client, normalized, extracted.images)
                if depth < self.job.max_depth:
                    for link in extracted.links:
                        if self._is_allowed(link):
                            queue.append((link, depth + 1))
                time.sleep(self.job.rate_limit_seconds)

        return CrawlResult(
            pages_seen=len(seen),
            pages_saved=pages_saved,
            images_saved=images_saved,
            output_dir=self.output_dir,
            warnings=warnings,
        )

    def _is_allowed(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return host in set(self.job.allowed_domains)

    def _matches_filters(self, url: str, title: str, text: str) -> bool:
        searchable = f"{url}\n{title}\n{text}"
        if self.job.include_url_patterns and not self._any_pattern_matches(
            self.job.include_url_patterns, url
        ):
            return False
        if self.job.include_text_patterns and not self._any_pattern_matches(
            self.job.include_text_patterns, searchable
        ):
            return False
        return not self._any_pattern_matches(self.job.exclude_text_patterns, searchable)

    def _any_pattern_matches(self, patterns: list[str], value: str) -> bool:
        for pattern in patterns:
            try:
                if search(pattern, value, flags=IGNORECASE):
                    return True
            except error:
                if pattern.lower() in value.lower():
                    return True
        return False

    def _robots_allowed(self, url: str) -> bool:
        if not self.job.respect_robots_txt:
            return True
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.robots_cache:
            parser = RobotFileParser()
            parser.set_url(f"{base}/robots.txt")
            try:
                parser.read()
            except Exception:
                return False
            self.robots_cache[base] = parser
        return self.robots_cache[base].can_fetch(self.settings.default_user_agent, url)

    def _save_page(self, url: str, title: str, text: str) -> None:
        if not self.job.include_text:
            return
        append_jsonl(
            self.output_dir / "raw" / "pages.jsonl",
            {"url": url, "title": title, "text": text},
        )

    def _save_images(self, client: httpx.Client, page_url: str, images: list[str]) -> int:
        saved = 0
        for image_url in images:
            if not self._is_allowed(image_url):
                continue
            try:
                response = client.get(image_url)
                response.raise_for_status()
            except httpx.HTTPError:
                continue
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                continue
            image_bytes = response.content
            if len(image_bytes) > self.settings.max_image_bytes:
                continue
            digest = sha256(image_bytes).hexdigest()
            suffix = self._image_suffix(image_url, content_type)
            image_path = self.output_dir / "raw" / "images" / f"{digest}{suffix}"
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(image_bytes)
            append_jsonl(
                self.output_dir / "raw" / "images.jsonl",
                {
                    "page_url": page_url,
                    "image_url": image_url,
                    "content_type": content_type,
                    "bytes": len(image_bytes),
                    "local_path": str(image_path.relative_to(self.output_dir)),
                    "sha256": digest,
                },
            )
            saved += 1
        return saved

    def _image_suffix(self, image_url: str, content_type: str) -> str:
        path_suffix = Path(unquote(urlparse(image_url).path)).suffix.lower()
        if path_suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}:
            return path_suffix
        return {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/avif": ".avif",
            "image/svg+xml": ".svg",
        }.get(content_type.split(";")[0].lower(), ".bin")
