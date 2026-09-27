import os
from openai import OpenAI

# Same OpenAI-compatible client shape works for many managed endpoints
client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ.get(
        "LLM_BASE_URL",
        "https://api.openai.com/v1",  # local/dev default
    ),
)
# Azure OpenAI: base_url like https://<resource>.openai.azure.com/openai/v1
# Nebius AI Studio: provider base_url from the console
# Bedrock: often a different SDK, abstract behind a thin adapter if you need it

print("client ready, base_url =", client.base_url)