from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from autotrain_data_forge import __version__
from autotrain_data_forge.api.ui import render_ui
from autotrain_data_forge.crawler import SafeCrawler
from autotrain_data_forge.llm import parse_request_heuristic, parse_request_with_llm
from autotrain_data_forge.schemas import (
    CrawlResult,
    HarvestJob,
    ParsePromptRequest,
    ParsedRequest,
    RetrievalHit,
    RetrievalQuery,
    SecurityFinding,
    TrainingResult,
)
from autotrain_data_forge.retrieval import LocalRetriever
from autotrain_data_forge.security import review_job
from autotrain_data_forge.training import LocalTrainer

app = FastAPI(
    title="AutoTrain Data Forge",
    version=__version__,
    description="Permissioned web data collection and local AI training service.",
)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return render_ui()


@app.get("/ui", response_class=HTMLResponse)
def ui() -> str:
    return render_ui()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.post("/v1/parse-request", response_model=ParsedRequest)
def parse_request(request: ParsePromptRequest) -> ParsedRequest:
    if request.llm:
        return parse_request_with_llm(request.prompt, request.llm)
    return parse_request_heuristic(request.prompt)


@app.post("/v1/review", response_model=list[SecurityFinding])
def review(job: HarvestJob) -> list[SecurityFinding]:
    return review_job(job)


@app.post("/v1/crawl", response_model=CrawlResult)
def crawl(job: HarvestJob, dry_run: bool = True) -> CrawlResult:
    return SafeCrawler(job, Path.cwd()).crawl(dry_run=dry_run)


@app.post("/v1/train", response_model=TrainingResult)
def train(job: HarvestJob) -> TrainingResult:
    return LocalTrainer(job, Path.cwd()).train()


@app.post("/v1/query", response_model=list[RetrievalHit])
def query(request: RetrievalQuery) -> list[RetrievalHit]:
    return LocalRetriever(request.model_dir).query(request.question, top_k=request.top_k)
