from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from autotrain_data_forge.schemas import HarvestJob


def load_job(path: Path) -> HarvestJob:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return HarvestJob.model_validate(data)


def write_job(path: Path, job: HarvestJob) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(job.model_dump(mode="json"), sort_keys=False), encoding="utf-8")


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

