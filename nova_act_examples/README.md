# Nova Act Examples

This directory contains examples demonstrating how to use Amazon Nova Act for web automation.

## Overview

Amazon Nova Act is a powerful web automation tool that enables you to create agents that interact with web pages. These examples showcase how to use Nova Act for various automation tasks, from basic web interactions to advanced parallel processing.

## Examples

### 1. Basic Example (`get_coffee_maker.py`)

A simple example that demonstrates the fundamentals of Nova Act:

- Initializing Nova Act with a starting web page (Amazon.com)
- Performing a simple search for "coffee maker"
- Selecting a search result
- Extracting information from a product page

Run this example to get familiar with the basic Nova Act workflow.

### 2. Advanced Example (`multi_monitor.py`)

A more complex example that demonstrates advanced Nova Act capabilities:

- Parallel execution of web tasks using ThreadPoolExecutor
- Searching for multiple monitor models simultaneously
- Extracting structured data (price, rating, size) from product pages
- Error handling for robust web automation
- Comparing results from multiple searches

This example shows how to scale web automation tasks for efficiency.

## Prerequisites

- Python 3.10 or higher
- A valid Nova Act API key (obtain from https://nova.amazon.com/act)
- Required Python packages (install from the main project's requirements.txt)

## Running the Examples

1. Make sure your Nova Act API key is set in your environment:
   ```bash
   export NOVA_ACT_API_KEY="your_api_key"
   ```

2. Run the basic example:
   ```bash
   python get_coffee_maker.py
   ```

3. Run the advanced example:
   ```bash
   python multi_monitor.py
   ```

## Key Concepts

- **Nova Act Initialization**: Each example demonstrates how to initialize Nova Act with appropriate parameters (starting page, video recording, headless mode).
- **Act Commands**: The examples use natural language commands with the `act()` method to instruct the browser.
- **Data Extraction**: Both examples show how to extract and process data from web pages.
- **Session Management**: The examples demonstrate proper handling of Nova Act sessions using context managers.
- **Parallel Execution**: The advanced example shows how to run multiple Nova Act instances in parallel for efficiency.

## Important Notes

- Nova Act creates browser logs and (optionally) video recordings in the `./logs` directory
- Headless mode runs browsers without a visible UI, which is useful for background automation
- For parallel execution, be mindful of resource usage when setting the number of workers 