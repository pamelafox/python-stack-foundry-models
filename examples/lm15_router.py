import os

from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from lm15 import LMRouter, Message, Request
from lm15.credentials import BearerToken
from lm15.router import RouterConfig

load_dotenv(override=True)

azure_token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"]),
    "https://ai.azure.com/.default",
)


model_choice = os.environ.get("MODEL_CHOICE", "openai")
if model_choice == "openai":
    model = f"openai:{os.environ['FOUNDRY_OPENAI_DEPLOYMENT']}"
elif model_choice == "claude":
    model = f"azure-anthropic:{os.environ['FOUNDRY_CLAUDE_DEPLOYMENT']}"
else:
    raise ValueError(f"Unsupported MODEL_CHOICE: {model_choice}")

router = LMRouter(
    RouterConfig(
        api_keys={
            "openai": lambda: BearerToken(azure_token_provider()),
            "azure-anthropic": lambda: BearerToken(azure_token_provider()),
        },
        base_urls={
            "openai": os.environ["FOUNDRY_MODELS_ENDPOINT"] + "/openai/v1",
        },
        settings={
            "azure-anthropic": {
                "resource": os.environ["FOUNDRY_RESOURCE_NAME"],
            },
        },
    )
)

response = router.complete(
    Request(
        model=model,
        messages=(Message.user("What is the capital of France?"),),
    )
)

print(response.text)
