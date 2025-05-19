import os

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Step 1: Define MCP stdio parameters
NOVA_ACT_API_KEY = os.getenv("NOVA_ACT_API_KEY")

nova_act_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["nova_act_mcp_server.py"],
            env={"NOVA_ACT_API_KEY": NOVA_ACT_API_KEY},
        ),
    )
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.7,
)

with nova_act_client:
    agent = Agent(
        tools=nova_act_client.list_tools_sync(),
        model=bedrock_model,
    )

    response = agent("Find the first backpack on amazon.com use headless mode")
