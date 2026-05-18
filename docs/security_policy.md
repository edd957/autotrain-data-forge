# Security Policy

AutoTrain Data Forge is designed for authorized data collection and local AI training. The project does not support bypassing authentication, scraping private areas, evading robots.txt, defeating rate limits, or deleting data from remote services.

## Guardrails

- Domain allowlists are required for every job.
- Localhost, loopback, link-local, and private-network IP targets are blocked by default.
- Only `http` and `https` URLs are supported.
- `robots.txt` is enforced by default and disabling it produces a high-severity finding.
- Output paths must stay inside the workspace.
- Rate limits and page limits are reviewed before collection.
- Image collection produces a rights-review finding and enforces a maximum download size.
- Cleanup policies delete only local files created by the job.
- LLM API keys are read from environment variables and are never written to job files.
- Base model configuration is reviewed for unknown license, path traversal, missing remote API key environment variables, and `trust_remote_code`.

## Responsible Use

Before running a job, confirm that you have permission to access, store, transform, and train on the selected data. Review website terms, licenses, privacy obligations, platform rules, and consent requirements.

## Unsupported Use

The project should not be used for:

- collecting credentials, tokens, payment data, private messages, or secrets;
- bypassing access controls, CAPTCHAs, paywalls, API limits, or robots.txt;
- scraping authenticated accounts without explicit permission;
- building datasets from copyrighted or personal data without a lawful basis;
- loading unreviewed remote model code or redistributing model weights without respecting their license;
- deleting or modifying data on remote websites.

## Reporting Issues

Open a GitHub issue with a clear reproduction, expected behavior, observed behavior, and any relevant job YAML. Do not include real API keys, credentials, private data, or proprietary datasets.
