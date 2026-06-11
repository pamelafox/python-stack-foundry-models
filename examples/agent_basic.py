import asyncio
import os

from azure.identity import AzureDeveloperCliCredential, get_bearer_token_provider
from dotenv import load_dotenv
from agent_framework_openai import OpenAIChatClient
from agent_framework.anthropic import AnthropicFoundryClient
from agent_framework import Agent

load_dotenv(override=True)

azure_credential = AzureDeveloperCliCredential(tenant_id=os.environ["AZURE_TENANT_ID"])

provider = "claude"
if provider == "openai":
    client = OpenAIChatClient(
        model=os.environ["FOUNDRY_OPENAI_DEPLOYMENT"],
        azure_endpoint=os.environ["FOUNDRY_MODELS_ENDPOINT"],
        credential=azure_credential,
    )
elif provider == "claude":
    token_provider = get_bearer_token_provider(azure_credential, "https://ai.azure.com/.default")
    client = AnthropicFoundryClient(
        model=os.environ["FOUNDRY_CLAUDE_DEPLOYMENT"],
        base_url=os.environ["FOUNDRY_MODELS_ENDPOINT"] + "/anthropic",
        azure_ad_token_provider=token_provider,
    )

agent = Agent(
    client=client,
    name="Assistant",
    instructions="You are a helpful assistant.",
)


async def main():
    response = await agent.run("What is the capital of France?")
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
