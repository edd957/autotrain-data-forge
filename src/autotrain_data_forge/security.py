from __future__ import annotations

import ipaddress
from pathlib import Path
from urllib.parse import urlparse

from autotrain_data_forge.schemas import (
    BaseModelProvider,
    CleanupPolicy,
    HarvestJob,
    SecurityFinding,
)


def review_job(job: HarvestJob, workspace: Path | None = None) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    workspace = workspace or Path.cwd()
    _review_domains(job, findings)
    _review_urls(job, findings)
    _review_output_path(job, workspace, findings)
    _review_limits(job, findings)
    _review_collection_policy(job, findings)
    _review_base_model(job, workspace, findings)
    return findings


def has_blocking_findings(findings: list[SecurityFinding]) -> bool:
    return any(finding.severity in {"critical", "high"} for finding in findings)


def _review_domains(job: HarvestJob, findings: list[SecurityFinding]) -> None:
    for domain in job.allowed_domains:
        if domain in {"localhost", "127.0.0.1", "0.0.0.0"}:
            findings.append(
                SecurityFinding(
                    severity="critical",
                    code="LOCALHOST_BLOCKED",
                    message="Localhost and loopback domains are blocked by default.",
                )
            )
        try:
            ip = ipaddress.ip_address(domain)
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            findings.append(
                SecurityFinding(
                    severity="critical",
                    code="PRIVATE_NETWORK_BLOCKED",
                    message=f"Private or local network target is blocked: {domain}",
                )
            )


def _review_urls(job: HarvestJob, findings: list[SecurityFinding]) -> None:
    allowed = set(job.allowed_domains)
    for seed in job.seeds:
        parsed = urlparse(seed)
        if parsed.scheme not in {"http", "https"}:
            findings.append(
                SecurityFinding(
                    severity="high",
                    code="UNSUPPORTED_SCHEME",
                    message=f"Only http and https URLs are supported: {seed}",
                )
            )
        host = (parsed.hostname or "").lower()
        if host not in allowed:
            findings.append(
                SecurityFinding(
                    severity="high",
                    code="DOMAIN_NOT_ALLOWED",
                    message=f"Seed host '{host}' is not in allowed_domains.",
                )
            )


def _review_output_path(
    job: HarvestJob,
    workspace: Path,
    findings: list[SecurityFinding],
) -> None:
    output_dir = job.output_dir
    if output_dir.is_absolute() or ".." in output_dir.parts:
        findings.append(
            SecurityFinding(
                severity="high",
                code="UNSAFE_OUTPUT_PATH",
                message="output_dir must be a relative path inside the workspace.",
            )
        )
        return
    resolved = (workspace / output_dir).resolve()
    if workspace.resolve() not in resolved.parents and resolved != workspace.resolve():
        findings.append(
            SecurityFinding(
                severity="high",
                code="WORKSPACE_ESCAPE",
                message=f"output_dir resolves outside workspace: {resolved}",
            )
        )


def _review_limits(job: HarvestJob, findings: list[SecurityFinding]) -> None:
    if job.max_pages > 100:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="LARGE_CRAWL_REVIEW",
                message="Crawls above 100 pages should be explicitly reviewed.",
            )
        )
    if job.rate_limit_seconds < 0.5:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="LOW_RATE_LIMIT",
                message="Consider a slower rate limit for respectful crawling.",
            )
        )
    if not job.respect_robots_txt:
        findings.append(
            SecurityFinding(
                severity="high",
                code="ROBOTS_DISABLED",
                message="robots.txt enforcement is disabled.",
            )
        )


def _review_collection_policy(job: HarvestJob, findings: list[SecurityFinding]) -> None:
    if job.include_images:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="IMAGE_RIGHTS_REVIEW",
                message="Image collection requires copyright, license, and consent review.",
            )
        )
    if job.cleanup_policy == CleanupPolicy.DELETE_ALL_AFTER_TRAINING:
        findings.append(
            SecurityFinding(
                severity="low",
                code="LOCAL_DELETION_NOTICE",
                message="Cleanup deletes only local collected data and generated artifacts.",
            )
        )
    if job.llm.provider != "none" and not job.llm.api_key_env:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="LLM_API_KEY_ENV_MISSING",
                message="LLM provider is enabled but api_key_env is empty.",
            )
        )


def _review_base_model(
    job: HarvestJob,
    workspace: Path,
    findings: list[SecurityFinding],
) -> None:
    base = job.base_model
    if base.provider == BaseModelProvider.NONE:
        return
    if base.trust_remote_code:
        findings.append(
            SecurityFinding(
                severity="high",
                code="BASE_MODEL_REMOTE_CODE",
                message="Base model requires trust_remote_code; review model code before use.",
            )
        )
    if not base.license_name:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="BASE_MODEL_LICENSE_UNKNOWN",
                message="Base model license is not declared.",
            )
        )
    if base.provider == BaseModelProvider.LOCAL_PATH:
        if base.local_path is None:
            findings.append(
                SecurityFinding(
                    severity="medium",
                    code="BASE_MODEL_PATH_MISSING",
                    message="Local base model provider requires local_path.",
                )
            )
            return
        if ".." in base.local_path.parts:
            findings.append(
                SecurityFinding(
                    severity="high",
                    code="BASE_MODEL_PATH_ESCAPE",
                    message="Local base model path must not contain parent directory traversal.",
                )
            )
        if not base.local_path.is_absolute():
            resolved = (workspace / base.local_path).resolve()
            if workspace.resolve() not in resolved.parents and resolved != workspace.resolve():
                findings.append(
                    SecurityFinding(
                        severity="high",
                        code="BASE_MODEL_WORKSPACE_ESCAPE",
                        message=f"Local base model path resolves outside workspace: {resolved}",
                    )
                )
    if base.provider == BaseModelProvider.OPENAI_COMPATIBLE and not base.api_key_env:
        findings.append(
            SecurityFinding(
                severity="medium",
                code="BASE_MODEL_API_KEY_ENV_MISSING",
                message="Remote base model provider is enabled but api_key_env is empty.",
            )
        )
