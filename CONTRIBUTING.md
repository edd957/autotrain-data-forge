# Contributing

Thanks for helping improve AutoTrain Data Forge.

## Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```

## Pull Requests

- Keep changes focused.
- Add tests for new behavior.
- Update docs and examples when user-facing behavior changes.
- Do not include real API keys, private data, or copyrighted datasets.
- Run security review logic against any new collection feature.
