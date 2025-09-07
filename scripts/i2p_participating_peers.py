#!/usr/bin/env python3

"""
I2P Participating Peers Data Extraction Script

This script fetches the I2P tunnels page from:
  http://127.0.0.1:7657/tunnels
It extracts data from the "Peers in multiple participating tunnels (including inactive)" 
section up to "Bandwidth Tiers". The extracted fields are:
  - Full Peer ID (from href)
  - Country (from flag title attribute)
  - Tunnels (number of tunnels)
  - Usage (bandwidth usage)
The extracted data is saved to a CSV file.
Requires: requests, beautifulsoup4, html5lib
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import csv
from datetime import datetime

# Configuration
URL = "http://127.0.0.1:7657/tunnels"
OUTPUT_DIR = "i2p_peer_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "i2p_participating_peers.csv")
FETCH_INTERVAL = 10   # seconds between fetches
TEST_DURATION = 300   # test duration in seconds (5 minutes)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize CSV file with headers if not exists
if not os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Full Peer ID", "Country", "Tunnels", "Usage"])

# Function to extract peer data from HTML
def extract_peer_data(html):
    soup = BeautifulSoup(html, "html5lib")

    # Find the specific section
    section_header = soup.find("h3", class_="tabletitle", text="Peers in multiple participating tunnels (including inactive)")
    if not section_header:
        print("Section not found.")
        return []

    # Locate the table following the header
    table = section_header.find_next("table", class_="tunneldisplay tunnels_participating")
    if not table:
        print("No table found.")
        return []

    rows = table.find_all("tr")[1:]  # Skip header row
    data = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        # Extract country from the first cell's <img> tag
        peer_cell = cells[0]
        img_tag = peer_cell.find("img")
        country = img_tag["title"] if img_tag and "title" in img_tag.attrs else "Unknown"

        # Extract full peer id from the <a> tag
        a_tag = peer_cell.find("a", title="NetDb entry")
        peer_id = a_tag["href"].split("netdb?r=")[-1] if a_tag else "Unknown"

        # Extract tunnels and usage
        tunnels = cells[1].get_text(strip=True)
        usage = cells[2].get_text(strip=True)

        data.append((peer_id, country, tunnels, usage))

    return data

print(f"Starting data capture from {URL} for {TEST_DURATION//60} minutes...")

start_time = time.time()
while time.time() - start_time < TEST_DURATION:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(URL, timeout=5)
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
            for record in extracted:
                peer_id, country, tunnels, usage = record
                writer.writerow([current_time, peer_id, country, tunnels, usage])
        print(f"[{current_time}] Captured {len(extracted)} peers. Example: Peer {extracted[0][0]}, Country {extracted[0][1]}")

    time.sleep(FETCH_INTERVAL)

print("Data capture test completed. Please check the output file for collected data.")
