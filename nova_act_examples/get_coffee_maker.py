import os

from nova_act import NovaAct

# make logs directory
os.makedirs("./logs", exist_ok=True)

# Initialize Nova Act with Amazon as the starting page
with NovaAct(starting_page="https://www.amazon.com", record_video=True, logs_directory="./logs") as n:
    # Perform a simple action - search for a product
    n.act("search for a coffee maker")
    # Click on a result
    n.act("select the first result")
    # Print the title of the page
    title = n.act("What is the title of this product page?")
    print(f"Product title: {title.response}")