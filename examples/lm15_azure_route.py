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

router = LMRouter(
    RouterConfig(
        api_keys={"azure": lambda: BearerToken(azure_token_provider())},
        settings={"azure": {"resource": os.environ["FOUNDRY_ACCOUNT_NAME"]}},
    )
)

response = router.complete(
    Request(
        model=f"azure:{os.environ['FOUNDRY_OPENAI_DEPLOYMENT']}",
        messages=(Message.user("What is the capital of France?"),),
    )
)

print(response.text)
