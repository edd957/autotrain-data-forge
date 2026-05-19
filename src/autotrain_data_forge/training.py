from __future__ import annotations

import json
import shutil
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from autotrain_data_forge.io import read_jsonl
from autotrain_data_forge.schemas import (
    BaseModelProvider,
    CleanupPolicy,
    HarvestJob,
    TrainingResult,
)


class LocalTrainer:
    """Train a lightweight local retrieval model from collected data."""

    def __init__(self, job: HarvestJob, workspace: Path | None = None) -> None:
        self.job = job
        self.workspace = workspace or Path.cwd()
        self.output_dir = self.workspace / job.output_dir
        self.model_dir = self.output_dir / "model"

    def train(self) -> TrainingResult:
        pages = read_jsonl(self.output_dir / "raw" / "pages.jsonl")
        image_records = read_jsonl(self.output_dir / "raw" / "images.jsonl")
        documents = [
            f"{record.get('title', '')}\n{record.get('url', '')}\n{record.get('text', '')}"
            for record in pages
            if record.get("text")
        ]
        documents.extend(
            f"Image reference from {record.get('page_url')}: {record.get('image_url')}"
            for record in image_records
        )
        if not documents:
            documents = [f"Empty dataset placeholder for job {self.job.name}."]

        self.model_dir.mkdir(parents=True, exist_ok=True)
        vectorizer = TfidfVectorizer(max_features=25_000, ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform(documents)
        joblib.dump(vectorizer, self.model_dir / "vectorizer.joblib")
        joblib.dump(matrix, self.model_dir / "matrix.joblib")
        (self.model_dir / "documents.json").write_text(
            json.dumps(documents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        manifest_path = self.output_dir / "dataset_manifest.json"
        training_card_path = self.output_dir / "training_card.md"
        base_model_plan_path = self.output_dir / "base_model_plan.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "job": self.job.model_dump(mode="json"),
                    "documents": len(documents),
                    "raw_pages": len(pages),
                    "image_references": len(image_records),
                    "base_model": self.job.base_model.model_dump(mode="json"),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        base_model_plan_path.write_text(
            json.dumps(self._base_model_plan(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        training_card_path.write_text(self._training_card(len(documents)), encoding="utf-8")
        self._cleanup()
        return TrainingResult(
            documents=len(documents),
            model_dir=self.model_dir,
            dataset_manifest=manifest_path,
            training_card=training_card_path,
            base_model_plan=base_model_plan_path,
        )

    def _training_card(self, documents: int) -> str:
        base = self.job.base_model
        return (
            f"# Training Card: {self.job.name}\n\n"
            f"- Goal: {self.job.goal}\n"
            f"- Documents: {documents}\n"
            f"- Seeds: {', '.join(self.job.seeds)}\n"
            f"- Allowed domains: {', '.join(self.job.allowed_domains)}\n"
            f"- Base model: {base.display_name} (`{base.provider.value}:{base.model_id}`)\n"
            f"- Base model task: {base.task.value}\n"
            f"- Base model license: {base.license_name or 'not declared'}\n"
            f"- Cleanup policy: {self.job.cleanup_policy.value}\n\n"
            "The default output is a local retrieval index trained from user-authorized data. "
            "If a base model is configured, review the base model plan before fine-tuning or "
            "adapting it with external tooling.\n"
        )

    def _base_model_plan(self) -> dict[str, object]:
        base = self.job.base_model
        return {
            "selected_base_model": base.model_dump(mode="json"),
            "default_trainer": "local_tfidf_retrieval",
            "integration_status": (
                "No external base model is loaded by the default trainer."
                if base.provider == BaseModelProvider.NONE
                else "Base model selected for downstream adaptation/export."
            ),
            "operator_review": [
                "Verify model license before training or redistribution.",
                "Confirm hardware requirements and quantization settings.",
                "Keep trust_remote_code disabled unless the model code has been reviewed.",
                "Do not upload private collected data to remote model providers without consent.",
            ],
        }

    def _cleanup(self) -> None:
        if self.job.cleanup_policy == CleanupPolicy.DELETE_RAW_AFTER_TRAINING:
            shutil.rmtree(self.output_dir / "raw", ignore_errors=True)
        if self.job.cleanup_policy == CleanupPolicy.DELETE_ALL_AFTER_TRAINING:
            shutil.rmtree(self.output_dir, ignore_errors=True)
