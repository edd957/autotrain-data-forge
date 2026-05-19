from autotrain_data_forge.llm import parse_request_heuristic


def test_heuristic_parser_builds_allowlisted_job_with_filters() -> None:
    parsed = parse_request_heuristic(
        'Collect text from https://example.com/news for posts mentioning "reviewed topic" '
        "and delete raw data after training."
    )

    assert parsed.job.seeds == ["https://example.com/news"]
    assert parsed.job.allowed_domains == ["example.com"]
    assert parsed.job.include_text_patterns == ["reviewed topic"]
    assert parsed.job.cleanup_policy.value == "delete_raw_after_training"


def test_heuristic_parser_detects_named_base_model() -> None:
    parsed = parse_request_heuristic(
        "Collect text from https://example.com/ and use TinyLlama/TinyLlama-1.1B-Chat-v1.0."
    )

    assert parsed.job.base_model.provider.value == "huggingface"
    assert parsed.job.base_model.task.value == "text_generation"
