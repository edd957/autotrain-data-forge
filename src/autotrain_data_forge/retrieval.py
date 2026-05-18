from __future__ import annotations

import json
from pathlib import Path

import joblib

from autotrain_data_forge.schemas import RetrievalHit


class LocalRetriever:
    """Query a local retrieval index produced by LocalTrainer."""

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir

    def query(self, question: str, top_k: int = 5) -> list[RetrievalHit]:
        vectorizer = joblib.load(self.model_dir / "vectorizer.joblib")
        matrix = joblib.load(self.model_dir / "matrix.joblib")
        documents = json.loads((self.model_dir / "documents.json").read_text(encoding="utf-8"))
        query_vector = vectorizer.transform([question])
        scores = (matrix @ query_vector.T).toarray().ravel()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]
        return [
            RetrievalHit(score=float(score), document=documents[index])
            for index, score in ranked
            if score > 0
        ]
