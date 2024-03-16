from selectorlib import Extractor
from plyer import notification
import requests
import json

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon=None,  # Path to an .ico file can be added if needed
        timeout=10,
    )

def scrape(url):  
    headers = {
        # Your headers...
    }

    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)
    
    if r.status_code > 500:
        # Your error handling...
        return None

    # Extract data with Extractor
    data = e.extract(r.text)
    
    # Now, combine the price_whole and price_fraction if they exist
    if 'price_whole' in data and 'price_fraction' in data:
        data['price'] = data['price_whole'].strip() + '.' + data['price_fraction'].strip()
        del data['price_whole']
        del data['price_fraction']

    return data

# Read the last recorded price if it exists
last_price = None
try:
    with open('last_price.txt', 'r') as file:
        last_price = file.read().strip()
except FileNotFoundError:
    print("No last recorded price.")

with open("urls.txt", 'r') as urllist, open('output.jsonl', 'w') as outfile:
    for url in urllist.read().splitlines():
        data = scrape(url) 
        if data:
            # Save the scraped data
            json.dump(data, outfile)
            outfile.write("\n")
            # If price has changed, send notification and update last_price.txt
            if data['price'] != last_price:
                send_notification('Amazon Price Update', f"The price of your item has changed to {data['price']}")
                with open('last_price.txt', 'w') as file:
                    file.write(data['price'])
            # Optional delay to prevent being blocked
            # sleep(5)
