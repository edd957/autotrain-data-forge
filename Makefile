.PHONY: test lint typecheck serve init review dry-run query

test:
	pytest

lint:
	ruff check .

typecheck:
	mypy src

serve:
	uvicorn autotrain_data_forge.api.main:app --host 0.0.0.0 --port 8020 --reload

init:
	adf init examples/generated_job.yml

review:
	adf review examples/authorized_docs.yml

dry-run:
	adf run examples/authorized_docs.yml --dry-run

query:
	adf query data/jobs/authorized-docs-demo/model "What did the dataset contain?"
