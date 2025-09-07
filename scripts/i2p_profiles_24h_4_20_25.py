#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I2P 24-Hour Peer Profiles Logger
Captures node metadata from: http://127.0.0.1:7657/profiles?f=1
"""

import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import re
from datetime import datetime

URL = "http://127.0.0.1:7657/profiles?f=1"
NETDB = "http://127.0.0.1:7657/netdb?r="
FETCH_INTERVAL = 300  # 5 minutes
RUN_DURATION = 24 * 60 * 60  # 24 hours

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "i2p_profiles_4_20_25")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "i2p_peer_profiles_24h_4_20_25.csv")

HEADERS = [
    "Timestamp", "Country", "Node Abbrev", "Full Node ID",
    "Groups", "Caps", "Version", "Speed", "Capacity", "Integration", "Status", "IP Address"
]

if not os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        csv.writer(f).writerow(HEADERS)

cache = {}
seen = set()

def get_node_ip(node_id):
    if node_id in cache:
        return cache[node_id]
    try:
        r = requests.get(NETDB + node_id, timeout=5)
        text = re.sub(r"<[^>]+>", " ", r.text)
        ipv4 = re.findall(r'(?i)host:\s*((?:\d{1,3}\.){3}\d{1,3})', text)
        ipv6 = re.findall(r'(?i)host:\s*((?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4})', text)
        ips = list(dict.fromkeys(ipv4 + ipv6))
        result = ";".join(ips) if ips else "Unknown"
    except Exception:
        result = "Error"
    cache[node_id] = result
    return result

print("[START] 24h peer profile capture...")

start = time.time()
while time.time() - start < RUN_DURATION:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[{now}] Error fetching profiles page: {e}")
        time.sleep(FETCH_INTERVAL)
        continue

    soup = BeautifulSoup(r.text, "html5lib")
    table = soup.find("table", id="profilelist")
    if not table:
        print(f"[{now}] Profile table not found.")
        time.sleep(FETCH_INTERVAL)
        continue

    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue

        # Peer Info
        peer_cell = cells[0]
        img = peer_cell.find("img")
        country = img.get("title", "Unknown") if img else "Unknown"

        a = peer_cell.find("a")
        abbrev = a.text.strip() if a else "Unknown"
        full_id = a.get("href", "").split("netdb?r=")[-1] if a else "Unknown"
        ip = get_node_ip(full_id)

        groups = cells[1].text.strip()
        caps = cells[2].text.strip()
        version = cells[3].text.strip()
        speed = cells[4].text.strip()
        capacity = cells[5].text.strip()
        integration = cells[6].text.strip()
        status = cells[7].text.strip()

        row_key = f"{full_id}-{version}-{status}"
        if row_key not in seen:
            seen.add(row_key)
            with open(OUTPUT_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    now, country, abbrev, full_id, groups, caps,
                    version, speed, capacity, integration, status, ip
                ])

    print(f"[{now}] Logged snapshot of peer profiles.")
    time.sleep(FETCH_INTERVAL)

print("[DONE] 24-hour peer profiles logging complete.")

