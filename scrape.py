import base64
import os
import time
import sys
import json

import requests
from bs4 import BeautifulSoup

def fetch_cached(url):
    url_key = base64.b64encode(url.encode()).decode()

    if os.path.isfile(f"cache/{url_key}"):
        print(f"Opening cached response {url}")
        with open(f"cache/{url_key}", 'r') as f:
            return f.read()
    else:
        print(f"Requesting {url}")
        time.sleep(0.5)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'}
        data = requests.get(url, headers=headers).text

        with open(f"cache/{url_key}", "w") as f:
            f.write(data)

        # Too short page: end of results or errors
        if len(data) < 1_000_000:
            #print(data)
            print(f"Page {url} too short, end of results/error?")
            return None

        return data

def get_one(l):
    assert len(l) == 1, l
    return l[0]

def parse_item(item_raw):
    title = get_one(item_raw.find_all('h3', attrs={'class': 's-item__title'})).get_text()
    price = item_raw.find_all('span', attrs={'class': 's-item__price'})[-1].get_text()
    location = get_one(item_raw.find_all('span', attrs={'class': 's-item__itemLocation'})).get_text()
    shipping = get_one(item_raw.find_all('span', attrs={'class': 's-item__logisticsCost'})).get_text()

    return {
        'title': title,
        'price': price,
        'location': location,
        'shipping': shipping,
    }

def get_items(query):
    items = []
    page = 1

    while True:
        url = f"https://www.ebay.com/sch/i.html?{query}&_ipg=200&_pgn={page}"
        html = fetch_cached(url)

        if not html:
            break

        soup = BeautifulSoup(html, features="html.parser")
    
        items_new = soup.find_all('div', attrs={'class': 's-item__wrapper'})

        for item_raw in items_new:
            items.append(parse_item(item_raw))

        page += 1
    return items
        

if __name__ == "__main__":
    with open('cache/intel.json', 'w') as f:
        json.dump(get_items("_nkw=intel+ssd&LH_BIN=1"), f)
    with open('cache/samsung.json', 'w') as f:
        json.dump(get_items("_nkw=samsung+ssd&LH_BIN=1"), f)
    with open('cache/hgst.json', 'w') as f:
        json.dump(get_items("_nkw=hgst+ssd&LH_BIN=1"), f)

