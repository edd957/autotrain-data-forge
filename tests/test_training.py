from pathlib import Path

from autotrain_data_forge.io import append_jsonl
from autotrain_data_forge.schemas import HarvestJob
from autotrain_data_forge.training import LocalTrainer


def test_trainer_writes_manifest_and_model(tmp_path: Path) -> None:
    job = HarvestJob(
        name="train-demo",
        goal="Train a local searchable assistant from public docs.",
        seeds=["https://example.com/"],
        allowed_domains=["example.com"],
        output_dir=Path("data/jobs/train-demo"),
    )
    append_jsonl(
        tmp_path / job.output_dir / "raw" / "pages.jsonl",
        {"url": "https://example.com/", "title": "Demo", "text": "Local AI training data"},
    )

    result = LocalTrainer(job, tmp_path).train()

    assert result.documents == 1
    assert (result.model_dir / "vectorizer.joblib").exists()
    assert result.dataset_manifest.exists()
    assert result.training_card.exists()
    assert result.base_model_plan is not None
    assert result.base_model_plan.exists()
