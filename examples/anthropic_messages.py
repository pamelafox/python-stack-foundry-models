import os

from anthropic import AnthropicFoundry
from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv(override=True)

endpoint = os.environ["FOUNDRY_MODELS_ENDPOINT"] + "/anthropic"
deployment_name = os.environ["FOUNDRY_CLAUDE_DEPLOYMENT"]
azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"])
token_provider = get_bearer_token_provider(azure_credential, "https://ai.azure.com/.default")

client = AnthropicFoundry(
    base_url=endpoint,
    azure_ad_token_provider=token_provider
)

message = client.messages.create(
    model=deployment_name,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    max_tokens=1024,
)

print(message.content)