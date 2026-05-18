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
