from __future__ import annotations

from autotrain_data_forge.schemas import BaseModelConfig, BaseModelProvider, BaseModelTask


BUILT_IN_MODELS: list[BaseModelConfig] = [
    BaseModelConfig(),
    BaseModelConfig(
        provider=BaseModelProvider.HUGGINGFACE,
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        display_name="MiniLM retrieval embeddings",
        task=BaseModelTask.RETRIEVAL,
        license_name="apache-2.0",
        parameters="22M",
        notes=["Small embedding model suitable for local retrieval experiments."],
    ),
    BaseModelConfig(
        provider=BaseModelProvider.HUGGINGFACE,
        model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        display_name="TinyLlama chat base",
        task=BaseModelTask.TEXT_GENERATION,
        license_name="apache-2.0",
        parameters="1.1B",
        notes=["Small open model example for local text-generation workflows."],
    ),
    BaseModelConfig(
        provider=BaseModelProvider.HUGGINGFACE,
        model_id="stabilityai/stable-diffusion-xl-base-1.0",
        display_name="Stable Diffusion XL base",
        task=BaseModelTask.IMAGE_GENERATION,
        license_name="openrail++",
        notes=["Image-generation base model example. Review license and hardware needs."],
    ),
    BaseModelConfig(
        provider=BaseModelProvider.OLLAMA,
        model_id="llama3.2",
        display_name="Ollama local text model",
        task=BaseModelTask.TEXT_GENERATION,
        endpoint="http://localhost:11434",
        notes=["Example local Ollama model id. Install and pull the model separately."],
    ),
]


def list_base_models(task: BaseModelTask | None = None) -> list[BaseModelConfig]:
    if task is None:
        return BUILT_IN_MODELS
    return [model for model in BUILT_IN_MODELS if model.task == task]


def find_base_model(model_id: str) -> BaseModelConfig | None:
    for model in BUILT_IN_MODELS:
        if model.model_id == model_id:
            return model
    return None
