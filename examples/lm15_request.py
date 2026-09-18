import os

from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from lm15 import AnthropicLM, Message, OpenAILM, Request
from lm15.access import AZURE_ANTHROPIC
from lm15.credentials import BearerToken

load_dotenv(override=True)

azure_token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"]),
    "https://ai.azure.com/.default",
)


model_choice = os.environ.get("MODEL_CHOICE", "openai")

if model_choice == "openai":
    lm = OpenAILM(
        api_key=lambda: BearerToken(azure_token_provider()),
        base_url=os.environ["FOUNDRY_MODELS_ENDPOINT"] + "/openai/v1",
    )
    model = os.environ["FOUNDRY_OPENAI_DEPLOYMENT"]
elif model_choice == "claude":
    lm = AnthropicLM(
        api_key=lambda: BearerToken(azure_token_provider()),
        access=AZURE_ANTHROPIC,
        settings={"resource": os.environ["FOUNDRY_RESOURCE_NAME"]},
    )
    model = os.environ["FOUNDRY_CLAUDE_DEPLOYMENT"]
else:
    raise ValueError(f"Unsupported MODEL_CHOICE: {model_choice}")

response = lm.complete(
    Request(
        model=model,
        messages=(Message.user("What is the capital of France?"),),
    )
)

print(response.text)
