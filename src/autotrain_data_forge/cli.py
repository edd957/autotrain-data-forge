from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from autotrain_data_forge.crawler import SafeCrawler
from autotrain_data_forge.io import load_job, write_job
from autotrain_data_forge.llm import parse_request_heuristic
from autotrain_data_forge.retrieval import LocalRetriever
from autotrain_data_forge.schemas import HarvestJob
from autotrain_data_forge.security import review_job
from autotrain_data_forge.training import LocalTrainer

app = typer.Typer(help="AutoTrain Data Forge CLI.")
console = Console()


@app.command("init")
def init_job(path: Path) -> None:
    job = HarvestJob(
        name="example-authorized-site",
        goal="Collect public documentation text for a local assistant.",
        seeds=["https://example.com/"],
        allowed_domains=["example.com"],
        output_dir="data/jobs/example-authorized-site",
    )
    write_job(path, job)
    console.print(f"Created job template at [bold]{path}[/bold]")


@app.command("parse-request")
def parse_request(prompt: str) -> None:
    parsed = parse_request_heuristic(prompt)
    console.print_json(parsed.model_dump_json())


@app.command("review")
def review(path: Path) -> None:
    findings = review_job(load_job(path), path.parent)
    console.print_json(json.dumps([finding.model_dump() for finding in findings]))


@app.command("run")
def run(path: Path, dry_run: bool = typer.Option(True, "--dry-run/--execute")) -> None:
    result = SafeCrawler(load_job(path), path.parent).crawl(dry_run=dry_run)
    console.print_json(result.model_dump_json())


@app.command("train")
def train(path: Path) -> None:
    result = LocalTrainer(load_job(path), path.parent).train()
    console.print_json(result.model_dump_json())


@app.command("query")
def query(model_dir: Path, question: str, top_k: int = 5) -> None:
    hits = LocalRetriever(model_dir).query(question, top_k=top_k)
    console.print_json(json.dumps([hit.model_dump() for hit in hits]))


@app.command("serve")
def serve() -> None:
    import uvicorn

    uvicorn.run("autotrain_data_forge.api.main:app", host="0.0.0.0", port=8020, reload=True)
