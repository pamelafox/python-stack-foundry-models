import os

from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from lm15 import Message, OpenAILM, Request
from lm15.credentials import BearerToken

load_dotenv(override=True)

azure_token_provider = get_bearer_token_provider(
    AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"]),
    "https://ai.azure.com/.default",
)


lm = OpenAILM(
    api_key=lambda: BearerToken(azure_token_provider()),
    base_url=os.environ["FOUNDRY_MODELS_ENDPOINT"] + "/openai/v1",
)

response = lm.complete(
    Request(
        model=os.environ["FOUNDRY_OPENAI_DEPLOYMENT"],
        messages=(Message.user("What is the capital of France?"),),
    )
)

print(response.text)
