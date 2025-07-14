#!/usr/bin/env python

import logging
import os

from botocore.config import Config
from mcp import stdio_client, StdioServerParameters

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient

# Set up logging
logger = logging.getLogger('__name__')
logging.getLogger("strands").setLevel(logging.INFO)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

HOME = os.getenv('HOME')
BEDROCK_REGION = os.getenv("BEDROCK_REGION", 'us-west-2')
BEDROCK_MODEL_ID = "us.amazon.nova-lite-v1:0"

# Amazon Location Services MCP Server
stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command = f'{HOME}/.local/bin/uvx',
        args = [ 'awslabs.aws-location-mcp-server@latest' ],
        env = {
          "AWS_REGION": BEDROCK_REGION,
          "FASTMCP_LOG_LEVEL": "ERROR"
        },
        disabled = False,
        autoApprove = []
    )
))

# Initialize Strands Agent
model = BedrockModel(
    model_id = BEDROCK_MODEL_ID,
    max_tokens = 2048,
    boto_client_config = Config(
        read_timeout = 120,
        connect_timeout = 120,
        retries = dict(max_attempts=3, mode="adaptive"),
    ),
    temperature = 0.1
)

LOCATION_SYSTEM_PROMPT = """
You are a chatbot assistant
You have access to the tool 'Amazon Location Services'
You should use the tool when users ask a question about maps, routing, or locations
"Example prompts where the user intent is relevant to Amazon Location Services include:
1. What is the latitude and longitude for {name of location}?
2. Provide the address for latitude: {latitude} and longitude: {longitude}.
"""

prompts = [
    "Give me the latitude and longitude for the IOI Building, Singapore 018916",
    "Provide the address for latitude: 1.27996 and longitude: 103.85121.",
    "What is the address for Singapore 018916"
]

def main():
    with stdio_mcp_client:
        tools = stdio_mcp_client.list_tools_sync()
        aws_location_agent = Agent(
            system_prompt = LOCATION_SYSTEM_PROMPT,
            model = model,
            tools = tools,
            # callback_handler = None
        )

        for prompt in prompts:
            print(f'**Prompt**: {prompt}')
            response = aws_location_agent(prompt)
            print('\n' + '-' * 80 + '\n')

if __name__ == '__main__':
    main()
