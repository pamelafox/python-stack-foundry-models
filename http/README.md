# HTTP examples

Standalone `.http` request files for calling the OpenAI Responses API and the
Anthropic Messages API directly through Microsoft Foundry, without any of the
Python SDKs. Run them with the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)
VS Code extension.

## Files

- [`openai_responses.http`](openai_responses.http) — calls the OpenAI Responses API.
- [`anthropic_messages.http`](anthropic_messages.http) — calls the Anthropic Messages API.
- [`auth.py`](auth.py) — mints a Microsoft Entra ID bearer token and writes it,
  along with the Foundry endpoint/deployment names, into `http/.env`.

## Prerequisites

- The REST Client VS Code extension installed.
- The repo-root [`.env`](../.env) file populated (via `azd provision`) with
  `AZURE_TENANT_ID`, `FOUNDRY_MODELS_ENDPOINT`, `FOUNDRY_OPENAI_DEPLOYMENT`,
  and `FOUNDRY_CLAUDE_DEPLOYMENT`.
- Signed in with `azd auth login` (or already signed in via the Azure Developer CLI).

## Usage

1. From the repo root, mint a fresh token and populate `http/.env`:

   ```bash
   uv run http/auth.py
   ```

   This creates/updates `http/.env` with `FOUNDRY_MODELS_ENDPOINT`,
   `FOUNDRY_OPENAI_DEPLOYMENT`, `FOUNDRY_CLAUDE_DEPLOYMENT`, and `TOKEN`.
   `http/.env` is git-ignored, so nothing sensitive gets committed.

2. Open `openai_responses.http` or `anthropic_messages.http` in VS Code and
   click **Send Request** above the request (REST Client adds this link
   automatically).

3. Bearer tokens expire after a while — if a request starts returning `401`,
   re-run `uv run http/auth.py` to refresh `http/.env` and try again.
