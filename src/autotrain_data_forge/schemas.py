from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class CleanupPolicy(StrEnum):
    RETAIN = "retain"
    DELETE_RAW_AFTER_TRAINING = "delete_raw_after_training"
    DELETE_ALL_AFTER_TRAINING = "delete_all_after_training"


class LLMProviderConfig(BaseModel):
    provider: str = "none"
    model: str = "none"
    api_key_env: str = "OPENAI_API_KEY"
    endpoint: str = "https://api.openai.com/v1/chat/completions"


class HarvestJob(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    goal: str = Field(min_length=10)
    seeds: list[str] = Field(min_length=1)
    allowed_domains: list[str] = Field(min_length=1)
    include_text: bool = True
    include_images: bool = False
    include_text_patterns: list[str] = Field(default_factory=list)
    exclude_text_patterns: list[str] = Field(default_factory=list)
    include_url_patterns: list[str] = Field(default_factory=list)
    max_pages: int = Field(default=25, ge=1, le=500)
    max_depth: int = Field(default=1, ge=0, le=5)
    rate_limit_seconds: float = Field(default=1.0, ge=0.1, le=60)
    respect_robots_txt: bool = True
    output_dir: Path = Path("data/jobs/default")
    cleanup_policy: CleanupPolicy = CleanupPolicy.RETAIN
    llm: LLMProviderConfig = Field(default_factory=LLMProviderConfig)

    @field_validator("allowed_domains")
    @classmethod
    def normalize_domains(cls, domains: list[str]) -> list[str]:
        return [domain.lower().strip() for domain in domains]


class SecurityFinding(BaseModel):
    severity: str
    code: str
    message: str


class CrawlResult(BaseModel):
    pages_seen: int
    pages_saved: int
    images_saved: int
    output_dir: Path
    warnings: list[str]


class TrainingResult(BaseModel):
    documents: int
    model_dir: Path
    dataset_manifest: Path
    training_card: Path


class ParsedRequest(BaseModel):
    job: HarvestJob
    notes: list[str]


class ParsePromptRequest(BaseModel):
    prompt: str = Field(min_length=10)
    llm: LLMProviderConfig | None = None


class RetrievalHit(BaseModel):
    score: float
    document: str


class RetrievalQuery(BaseModel):
    model_dir: Path
    question: str = Field(min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)
