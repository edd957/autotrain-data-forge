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


class BaseModelProvider(StrEnum):
    NONE = "none"
    HUGGINGFACE = "huggingface"
    LOCAL_PATH = "local_path"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"
    CUSTOM = "custom"


class BaseModelTask(StrEnum):
    RETRIEVAL = "retrieval"
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    MULTIMODAL = "multimodal"


class ModelPrecision(StrEnum):
    AUTO = "auto"
    FP32 = "fp32"
    FP16 = "fp16"
    BF16 = "bf16"
    INT8 = "int8"
    INT4 = "int4"


class BaseModelConfig(BaseModel):
    provider: BaseModelProvider = BaseModelProvider.NONE
    model_id: str = "none"
    display_name: str = "No external base model"
    task: BaseModelTask = BaseModelTask.RETRIEVAL
    revision: str | None = None
    local_path: Path | None = None
    endpoint: str | None = None
    api_key_env: str | None = None
    license_name: str | None = None
    precision: ModelPrecision = ModelPrecision.AUTO
    context_window: int | None = Field(default=None, ge=1)
    parameters: str | None = None
    trust_remote_code: bool = False
    notes: list[str] = Field(default_factory=list)
    extra_config: dict[str, str] = Field(default_factory=dict)


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
    base_model: BaseModelConfig = Field(default_factory=BaseModelConfig)

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
    base_model_plan: Path | None = None


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
