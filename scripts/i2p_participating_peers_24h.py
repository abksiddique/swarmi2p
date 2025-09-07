#!/usr/bin/env python3

"""
I2P 24-Hour Dynamic Peer Data Extraction Script

This script runs for **24 hours in the background** capturing **I2P peer data**
from the "Peers in multiple participating tunnels (including inactive)" section
on **http://127.0.0.1:7657/tunnels**. It **only logs new data** when:
  - A **new peer** appears
  - A peer’s **tunnel count changes** (e.g., 40 tunnels → 70 tunnels)

Captured fields:
  - **Full Peer ID** (from href)
  - **Country** (from flag title attribute)
  - **Tunnels** (number of tunnels)
  - **Usage** (bandwidth usage)
  - **Timestamp** (when the change was captured)

Saves output to `i2p_participating_peers_24h.csv`

Runs in the background using `nohup` to prevent termination when closing the terminal.

Requires: `requests`, `beautifulsoup4`, `html5lib`
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import csv
from datetime import datetime

# Configuration
URL = "http://127.0.0.1:7657/tunnels"
OUTPUT_DIR = "i2p_peer_data2"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "i2p_participating_peers_24h.csv")
FETCH_INTERVAL = 60  # Fetch every 60 seconds
RUN_DURATION = 24 * 60 * 60  # 24 hours in seconds

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize CSV file if it does not exist
if not os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Full Peer ID", "Country", "Tunnels", "Usage"])

# Track last known data for each peer
peer_data_history = {}

# Function to extract peer data
def extract_peer_data(html):
    soup = BeautifulSoup(html, "html5lib")

    # Locate the target section
    section_header = soup.find("h3", class_="tabletitle", text="Peers in multiple participating tunnels (including inactive)")
    if not section_header:
        print("Section not found.")
        return {}

    # Locate the table
    table = section_header.find_next("table", class_="tunneldisplay tunnels_participating")
    if not table:
        print("No table found.")
        return {}

    rows = table.find_all("tr")[1:]  # Skip header row
    extracted_data = {}

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        # Extract country
        peer_cell = cells[0]
        img_tag = peer_cell.find("img")
        country = img_tag["title"] if img_tag and "title" in img_tag.attrs else "Unknown"

        # Extract full peer id
        a_tag = peer_cell.find("a", title="NetDb entry")
        peer_id = a_tag["href"].split("netdb?r=")[-1] if a_tag else "Unknown"

        # Extract tunnels and usage
        tunnels = cells[1].get_text(strip=True)
        usage = cells[2].get_text(strip=True)

        extracted_data[peer_id] = (country, tunnels, usage)

    return extracted_data

# Start capture
print(f"Starting 24-hour data capture from {URL}...")

start_time = time.time()
while time.time() - start_time < RUN_DURATION:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[{current_time}] Error fetching URL: {e}")
        time.sleep(FETCH_INTERVAL)
        continue

    html = response.text
    extracted = extract_peer_data(html)

    if not extracted:
        print(f"[{current_time}] WARNING: No peer data extracted.")
    else:
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            new_count = 0
            for peer_id, (country, tunnels, usage) in extracted.items():
                # Only capture if the peer is new or tunnels count has changed
                if peer_id not in peer_data_history or peer_data_history[peer_id][1] != tunnels:
                    peer_data_history[peer_id] = (country, tunnels, usage)
                    writer.writerow([current_time, peer_id, country, tunnels, usage])
                    new_count += 1

        print(f"[{current_time}] Captured {new_count} updates.")

    time.sleep(FETCH_INTERVAL)

print("24-hour data capture completed. Check the CSV file for collected data.")
