#!/bin/env python3

import glob
import json
import os
import re

def guess_capacity(title):
    #matches = re.findall("([0-9.]{1,4})[^0-9]?([GT])", title.replace(',', ''), re.IGNORECASE)
    matches = re.findall("([0-9][0-9.]{0,3})[^0-9]?([GT])", title.replace(',', ''), re.IGNORECASE)

    guess_gigabytes = None
    for size, unit in matches:
        base_size = float(size)
        if 'T' in unit.upper():
            gigabytes = 1000 * base_size
        else:
            gigabytes = base_size

        # Do not confuse with 6 or 12 Gb/s
        if gigabytes < 16:
            continue

        # Same goes for 9000 TBW
        if gigabytes > 10_000:
            continue

        else:
            guess_gigabytes = gigabytes

    return guess_gigabytes

VAT_countries = ["Austria","Belgium","Bulgaria","Cyprus","Czech Republic","Croatia","Denmark","Estonia","Finland","France","Monaco","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden"]

def get_price(item):
    item_price = float(item['price'].replace('EUR ', '').replace(',', ''))

    if 'EUR' in item['shipping']:
        shipping_cost = float(item['shipping'].split(' ')[1])
    elif 'Free Int' in item['shipping']:
        shipping_cost = 0
    else:
        return None

    country = ' '.join(item['location'].split(' ')[1:])
    if country not in VAT_countries:
        multiplier = 1.00
    else:
        multiplier = 1.24

    #print(country, item_price, shipping_cost, multiplier)

    return multiplier * (item_price + shipping_cost)

files = glob.glob('cache/*.json')
for filename in files:
    with open(filename, 'r') as f:
        items = json.load(f)

    for item in items:
        if ' to ' in item['price']:
            # Not supported for now
            continue
        total_price = get_price(item)
        capacity = guess_capacity(item['title'])

        if None in (total_price, capacity):
            print("Unable to parse:", item)
            continue
        
        price_per_gb = total_price / capacity

        print(f"{price_per_gb:.4f} - {item}")
