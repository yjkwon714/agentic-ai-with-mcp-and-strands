import time
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from nova_act import NovaAct

# make logs directory
os.makedirs("./logs", exist_ok=True)

def check_monitor_on_amazon(monitor_model, headless=True):
    """Search for a specific monitor model on Amazon and extract information"""
    # Create a unique ID for this thread's browser session
    session_id = uuid.uuid4().hex[:8]
    print(f"[Thread {session_id}] Starting search for {monitor_model}")

    results = {"model": monitor_model, "price": "N/A", "rating": "N/A", "size": "N/A"}

    try:
        # Each thread gets its own isolated browser session
        with NovaAct(
            starting_page="https://www.amazon.com",
            record_video=True,
            headless=headless,
            logs_directory="./logs",
        ) as n:
            print(f"[Thread {session_id}] Browser session started")

            # Search for the specific monitor model
            n.act(f"search for '{monitor_model}'")

            # Click on the first result
            n.act("click on the first search result")

            # Get the price
            price_result = n.act("What is the current price of this monitor?")
            results["price"] = price_result.response

            # Get the rating
            rating_result = n.act("What is the average rating of this monitor?")
            results["rating"] = rating_result.response

            # Get screen size
            size_result = n.act("What is the screen size of this monitor?")
            results["size"] = size_result.response

        print(f"[Thread {session_id}] ✅ Completed search for {monitor_model}")
    except Exception as e:
        print(f"[Thread {session_id}] ❌ Error searching for {monitor_model}: {e}")

    return results


def parallel_monitor_comparison():
    # List of popular monitor models to check
    monitor_models = [
        "Dell S2722QC 27-inch 4K USB-C Monitor",
        "LG 27GP850-B 27-inch Ultragear Gaming Monitor",
        "Samsung Odyssey G7 32-inch Gaming Monitor",
    ]

    all_results = []
    start_time = time.time()

    # Execute searches in parallel with proper error handling
    # Use fewer workers to avoid resource contention
    max_workers = min(3, len(monitor_models))
    print(f"Starting parallel execution with {max_workers} workers")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all search tasks - each gets a fresh NovaAct instance
        future_to_model = {
            executor.submit(check_monitor_on_amazon, model, True): model
            for model in monitor_models
        }

        # Process results as they complete
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                results = future.result()
                all_results.append(results)
            except Exception as e:
                print(f"❌ Error processing results for {model}: {e}")

    elapsed = time.time() - start_time
    print(f"Parallel execution completed in {elapsed:.2f} seconds")

    # Print comparison table
    print("\nMonitor Comparison:")
    print("-" * 80)
    print(f"{'Model':<30} {'Price':<10} {'Rating':<10} {'Size':<10}")
    print("-" * 80)
    for result in all_results:
        print(
            f"{result['model'][:28]:<30} {result['price']:<10} {result['rating']:<10} {result['size']:<10}"
        )

    return all_results


if __name__ == "__main__":
    parallel_monitor_comparison()

