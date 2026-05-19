from autotrain_data_forge.model_catalog import find_base_model, list_base_models
from autotrain_data_forge.schemas import BaseModelTask


def test_catalog_lists_text_generation_models() -> None:
    models = list_base_models(BaseModelTask.TEXT_GENERATION)

    assert models
    assert all(model.task == BaseModelTask.TEXT_GENERATION for model in models)


def test_catalog_finds_model_by_id() -> None:
    model = find_base_model("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

    assert model is not None
    assert model.provider.value == "huggingface"
