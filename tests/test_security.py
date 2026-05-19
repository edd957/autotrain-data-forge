from pathlib import Path

from autotrain_data_forge.schemas import BaseModelConfig, HarvestJob
from autotrain_data_forge.security import has_blocking_findings, review_job


def test_review_blocks_private_network_targets() -> None:
    job = HarvestJob(
        name="private-target",
        goal="Collect public text from a safe site.",
        seeds=["http://127.0.0.1/admin"],
        allowed_domains=["127.0.0.1"],
    )

    findings = review_job(job)

    assert has_blocking_findings(findings)
    assert {finding.code for finding in findings} >= {
        "LOCALHOST_BLOCKED",
        "PRIVATE_NETWORK_BLOCKED",
    }


def test_review_blocks_output_path_escape(tmp_path: Path) -> None:
    job = HarvestJob(
        name="escape",
        goal="Collect public text from a safe site.",
        seeds=["https://example.com/"],
        allowed_domains=["example.com"],
        output_dir=Path("../outside"),
    )

    findings = review_job(job, tmp_path)

    assert any(finding.code == "UNSAFE_OUTPUT_PATH" for finding in findings)


def test_review_flags_unreviewed_base_model_code() -> None:
    job = HarvestJob(
        name="remote-code",
        goal="Collect public text from a safe site.",
        seeds=["https://example.com/"],
        allowed_domains=["example.com"],
        base_model=BaseModelConfig(
            provider="huggingface",
            model_id="example/needs-code",
            display_name="Needs remote code",
            trust_remote_code=True,
        ),
    )

    findings = review_job(job)

    assert any(finding.code == "BASE_MODEL_REMOTE_CODE" for finding in findings)
