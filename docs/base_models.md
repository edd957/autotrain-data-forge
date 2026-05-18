# Base Models

AutoTrain Data Forge lets a user choose an optional base AI model in each job. This supports workflows where collected, authorized data is prepared for a known open-source model, local model, Ollama model, or OpenAI-compatible endpoint.

The default trainer still builds a lightweight local retrieval index. External base models are not loaded automatically. Instead, the selected model is written into audit artifacts so the operator can decide how to fine-tune, adapt, export, or query with separate tooling.

## List Built-In Examples

```bash
adf models
adf models --task retrieval
adf models --task text_generation
```

API:

```bash
curl http://localhost:8020/v1/base-models
```

## YAML Schema

```yaml
base_model:
  provider: huggingface
  model_id: TinyLlama/TinyLlama-1.1B-Chat-v1.0
  display_name: TinyLlama chat base
  task: text_generation
  revision: null
  local_path: null
  endpoint: null
  api_key_env: null
  license_name: apache-2.0
  precision: int4
  context_window: 2048
  parameters: 1.1B
  trust_remote_code: false
  notes:
    - Review model license and hardware requirements before adaptation.
  extra_config: {}
```

## Providers

- `none`: no external model is selected.
- `huggingface`: model id from an open model registry.
- `local_path`: model files already exist on the operator machine.
- `ollama`: local Ollama model id and endpoint.
- `openai_compatible`: remote model endpoint that follows a chat-completion style API.
- `custom`: user-defined integration metadata.

## Safety Review

The security review warns on unknown licenses, local path issues, remote API key configuration, and `trust_remote_code`. Keep `trust_remote_code` disabled unless the model repository code has been manually reviewed.
