from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("hello-world-server")


# Define tools
@mcp.tool()
async def greet(name: str) -> str:
    """Greet a person with their name.

    Parameters:
        name: The name of the person to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}! Welcome to MCP."


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two numbers together.

    Parameters:
        a: First number
        b: Second number

    Returns:
        The sum of the two numbers
    """
    return a + b


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first.

    Parameters:
        a: First number
        b: Second number to subtract from the first

    Returns:
        The difference between the two numbers
    """
    return a - b


@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.

    Parameters:
        a: First number
        b: Second number

    Returns:
        The product of the two numbers
    """
    return a * b


@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Divide the first number by the second.

    Parameters:
        a: Numerator
        b: Denominator

    Returns:
        The result of the division
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@mcp.tool()
async def tell_joke() -> str:
    """Tell a programming joke.

    Returns:
        A programming joke
    """
    return "Why do programmers prefer dark mode? Because light attracts bugs!"


# Run the server
if __name__ == "__main__":
    print("Starting Hello World MCP Server...")
    print("This server provides simple greeting and calculator tools.")
    print("Connect to this server using an MCP client to interact with these tools.")
    print("Press Ctrl+C to stop the server.")

    # Start the server
    mcp.run()
