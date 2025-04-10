# MCP Nova Act Server

An MCP (Model Context Protocol) server implementation for Amazon Nova Act, allowing LLMs to control web browsers through a standardized MCP interface.

## Features

- Execute browser actions through natural language instructions
- Run parallel tasks across multiple browser instances
- Capture and store action results
- Take screenshots of browser sessions
- Save results to JSON files for later analysis

## Prerequisites

1. Operating System: MacOS or Ubuntu (Nova Act requirements)
2. Python 3.10 or above
3. A valid Nova Act API key (obtain from https://nova.amazon.com/act)
4. Amazon Bedrock access:
   - Amazon Bedrock enabled in your AWS account
   - Claude 3.5 Sonnet V2 model enabled and set as default
   - AWS credentials and region properly configured

## Installation

1. Install dependencies from main folder:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Nova Act API key as an environment variable:
   ```bash
   export NOVA_ACT_API_KEY="your_api_key"
   ```

3. Configure AWS credentials following the [AWS CLI Quickstart Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)

## Usage

### Starting the Client and Server

```bash
python nova_act_mcp_client.py nova_act_mcp_server.py
```

This command will:
1. Start the MCP server that exposes Nova Act capabilities
2. Launch the MCP client that connects to the server
3. Enable communication between Claude and the Nova Act browser automation

## Claude Desktop Integration

For setting up and using this server with Claude Desktop, please follow the official [Claude Desktop MCP Setup Guide](https://modelcontextprotocol.io/quickstart/user).

## Writing Effective Nova Act Instructions

When writing actions for Nova Act:

1. Be prescriptive and succinct
   ✅ "Click the hamburger menu icon, go to Order History"
   ❌ "Find my order history"

2. Break complex tasks into smaller actions
   ✅ "Search for hotels in Houston", then "Sort by avg customer review"
   ❌ "Find the highest rated hotel in Houston"

3. Be specific about UI elements
   ✅ "Scroll down until you see 'add to cart' and then click it"
   ❌ "Add the item to cart"

4. For data extraction, use dedicated actions with schemas
   ✅ "Return the product name, price, and rating"
   ❌ "Tell me about this product"

## Best Practices

1. Always close browser sessions when done to free up resources
2. Use headless mode for automated tasks that don't require visual feedback
3. Break down complex actions into smaller, more specific instructions
4. Use schemas when expecting structured data responses
5. Save important results to files for persistence
6. Handle errors appropriately in your client code

## Troubleshooting

- If browser sessions fail to start, check your Nova Act API key
- For parallel execution issues, try reducing the number of concurrent tasks
- Browser performance problems may indicate insufficient system resources
- If actions are not working as expected, try making them more specific and explicit
