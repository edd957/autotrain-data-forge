# LLM Providers

AutoTrain Data Forge can use an OpenAI-compatible chat endpoint to draft safe collection jobs from natural language. The LLM is optional. The local heuristic parser works without an API key.

## Environment Variables

```bash
export OPENAI_API_KEY="your-key"
```

On Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

## YAML Configuration

```yaml
llm:
  provider: openai_compatible
  model: gpt-4.1-mini
  api_key_env: OPENAI_API_KEY
  endpoint: https://api.openai.com/v1/chat/completions
```

## Privacy Notes

The LLM planner receives the user's planning prompt. Crawled page contents are not sent to the LLM by the default pipeline. Keep prompts free of secrets and review generated jobs before execution.
