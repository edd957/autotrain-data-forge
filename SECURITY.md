# Security

If you find a security issue, please open a private report if GitHub private vulnerability reporting is enabled, or create a minimal public issue without sensitive details.

Never include live credentials, private data, access tokens, cookies, or proprietary datasets in an issue, pull request, or test fixture.

The project currently treats the following as security-sensitive:

- URL parsing and SSRF prevention;
- robots.txt enforcement;
- API key handling;
- cleanup policy boundaries;
- image download limits;
- LLM prompt-to-job conversion.
