from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx

from autotrain_data_forge.schemas import CleanupPolicy, HarvestJob, LLMProviderConfig, ParsedRequest


URL_PATTERN = re.compile(r"https?://[^\s,\"')>]+")


def parse_request_heuristic(prompt: str) -> ParsedRequest:
    urls = [url.rstrip(".,;]") for url in URL_PATTERN.findall(prompt)]
    domains = sorted({urlparse(url).hostname or "" for url in urls})
    include_images = any(word in prompt.lower() for word in ["image", "images", "photo", "photos"])
    cleanup_policy = (
        CleanupPolicy.DELETE_RAW_AFTER_TRAINING
        if "delete" in prompt.lower()
        else CleanupPolicy.RETAIN
    )
    quoted_filters = re.findall(r'"([^"]+)"|' + r"'([^']+)'", prompt)
    include_text_patterns = [
        value
        for first, second in quoted_filters
        if (value := first or second) and not value.startswith("http")
    ]
    job = HarvestJob(
        name="llm-planned-job",
        goal=prompt[:300],
        seeds=urls or ["https://example.com/"],
        allowed_domains=domains or ["example.com"],
        include_text=True,
        include_images=include_images,
        include_text_patterns=include_text_patterns,
        max_pages=25,
        max_depth=1,
        output_dir=Path("data/jobs/llm-planned-job"),
        cleanup_policy=cleanup_policy,
    )
    notes = ["Heuristic parser used. Review domains, rights, and dataset scope before crawling."]
    return ParsedRequest(job=job, notes=notes)


def parse_request_with_llm(prompt: str, config: LLMProviderConfig) -> ParsedRequest:
    api_key = os.getenv(config.api_key_env)
    if not api_key or config.provider == "none":
        return parse_request_heuristic(prompt)
    system_prompt = (
        "Create a safe web data collection job. Only include user-provided URLs. "
        "Respect robots.txt, use allowlisted domains, and never suggest bypassing access controls. "
        "Return concise JSON fields: name, goal, seeds, allowed_domains, "
        "include_images, max_pages, "
        "max_depth, output_dir, cleanup_policy, include_text_patterns, exclude_text_patterns."
    )
    response = httpx.post(
        config.endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        },
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    heuristic = parse_request_heuristic(content)
    heuristic.notes.append("LLM response was normalized through the local safety parser.")
    return heuristic
