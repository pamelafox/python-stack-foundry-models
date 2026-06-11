# Instructions for coding agents

This repository contains samples showing different Python stacks (OpenAI SDK, Anthropic SDK, LiteLLM, PydanticAI, Microsoft Agent Framework) for building on top of multiple Microsoft Foundry models (OpenAI, Claude, etc).

All examples authenticate to Foundry using `AzureDeveloperCliCredential` and reference environment variables from a `.env` file (produced by `azd provision`).

Key SDKs/frameworks used:
- **OpenAI Python SDK** (`openai`): For calling Foundry-hosted OpenAI models via the Responses API.
- **Anthropic Python SDK** (`anthropic`): For calling Foundry-hosted Claude models via the Messages API.
- **LiteLLM** (`litellm`): A unified interface that abstracts provider differences.
- **PydanticAI** (`pydantic-ai`): Agent framework with typed tool support, works with OpenAI or Anthropic providers.
- **Microsoft Agent Framework** (`agent-framework-*`): Microsoft's agent framework, supporting OpenAI and Anthropic clients.

The Microsoft Agent Framework (MAF) GitHub repo is here:
https://github.com/microsoft/agent-framework
The Python changelog is here:
https://github.com/microsoft/agent-framework/blob/main/python/CHANGELOG.md
MAF documentation: https://learn.microsoft.com/agent-framework/

## Package management

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Use `uv` commands instead of `pip`:

```bash
uv add <package>
uv sync
```

## Debugging Azure Python SDK HTTP requests

When debugging HTTP interactions between Azure Python SDKs (like `azure-ai-evaluation`) and Azure services, there are three levels of logging you can enable:

### 1. Azure SDK logger (request headers and URLs)

Set the Azure SDK loggers to DEBUG level to see request URLs, headers, and status codes:

```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("azure").setLevel(logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.DEBUG)
```

### 2. Raw HTTP wire data (request/response headers)

Enable `http.client` debug logging to see the raw HTTP wire protocol, including request and response headers:

```python
import http.client
http.client.HTTPConnection.debuglevel = 1
```

Note: Response bodies will typically not be visible at this level because Azure SDKs use gzip compression, and `http.client` logs the raw compressed bytes.

### 3. Decompressed response bodies

To see actual response bodies, monkey-patch the Azure SDK's `HttpLoggingPolicy.on_response` method. This works because `response.http_response.body()` returns the decompressed content:

```python
from azure.core.pipeline.policies import HttpLoggingPolicy

_original_on_response = HttpLoggingPolicy.on_response

def _on_response_with_body(self, request, response):
    _original_on_response(self, request, response)
    try:
        body = response.http_response.body()
        if body:
            _logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
            _logger.debug("Response body: %s", body[:4096].decode("utf-8", errors="replace"))
    except Exception:
        pass

HttpLoggingPolicy.on_response = _on_response_with_body
```
