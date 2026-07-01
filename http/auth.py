import os
from pathlib import Path

from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables from the repo-root .env file (for AZURE_TENANT_ID).
# Passed explicitly because find_dotenv()'s auto-discovery would otherwise stop
# at this folder's own .env (which only holds TOKEN) before reaching the root one.
repo_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(repo_root_env, override=True)

# Get a token from Azure, using the same credential/scope as the other examples
azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"])
token_provider = get_bearer_token_provider(azure_credential, "https://ai.azure.com/.default")
token = token_provider()

# Values copied from the repo-root .env into http/.env, alongside the token,
# so the .http files only need to read variables from this one file.
copied_vars = {
    "FOUNDRY_MODELS_ENDPOINT": os.environ["FOUNDRY_MODELS_ENDPOINT"],
    "FOUNDRY_OPENAI_DEPLOYMENT": os.environ["FOUNDRY_OPENAI_DEPLOYMENT"],
    "FOUNDRY_CLAUDE_DEPLOYMENT": os.environ["FOUNDRY_CLAUDE_DEPLOYMENT"],
}

# Path to the http/.env file (this script lives in http/, alongside the .http files)
env_path = Path(__file__).parent / ".env"

# Read the existing lines, if the file already exists
lines = []
if env_path.exists():
    with open(env_path) as f:
        lines = f.readlines()

managed_keys = ("TOKEN=", *(f"{key}=" for key in copied_vars))

# Write back untouched lines and append the freshly minted values
with open(env_path, "w") as f:
    for line in lines:
        if not line.startswith(managed_keys):
            f.write(line)
    for key, value in copied_vars.items():
        f.write(f"{key}={value}\n")
    f.write(f"TOKEN={token}\n")

print(f"Wrote fresh TOKEN to {env_path}")

