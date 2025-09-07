#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I2P 24-Hour Client Tunnel Peer Logger
Captures detailed node info (ID, country, IP) from the
"Client tunnels for shared clients" section on the I2P console.
"""

import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import re
from datetime import datetime

URL = "http://127.0.0.1:7657/tunnels"
NETDB_URL = "http://127.0.0.1:7657/netdb?r="
FETCH_INTERVAL = 60  # in seconds
RUN_DURATION = 24 * 60 * 60  # 24 hours

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "i2p_client_tunnels_data_4_19_25")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "i2p_client_tunnels_24h_4_19_25.csv")

CSV_HEADERS = [
    "Timestamp", "Direction", "Expiration", "Usage",
    "Node Role", "Node Abbrev", "Full ID", "Country", "IP Address"
]

if not os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        csv.writer(f).writerow(CSV_HEADERS)

node_cache = {}

def get_node_ip(node_id):
    if node_id in node_cache:
        return node_cache[node_id]

    try:
        resp = requests.get(NETDB_URL + node_id, timeout=5)
        html = re.sub(r'<[^>]+>', ' ', resp.text)
        ipv4 = re.findall(r'(?i)host:\s*((?:\d{1,3}\.){3}\d{1,3})', html)
        ipv6 = re.findall(r'(?i)host:\s*((?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4})', html)
        ip_list = list(dict.fromkeys(ipv4 + ipv6))
        result = ";".join(ip_list) if ip_list else "Unknown"
    except Exception:
        result = "Error"
    node_cache[node_id] = result
    return result

seen = set()
print(f"[START] Capturing from {URL} for 24 hours...")

start_time = time.time()
while time.time() - start_time < RUN_DURATION:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"[{now}] ERROR fetching tunnels page: {e}")
        time.sleep(FETCH_INTERVAL)
        continue

    soup = BeautifulSoup(res.text, "html5lib")
    header = soup.find("h3", id="UsNd")
    table = header.find_next("table", class_="tunneldisplay") if header else None
    if not table:
        print(f"[{now}] No table found for client tunnels.")
        time.sleep(FETCH_INTERVAL)
        continue

    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        direction = cells[0].find("img")["alt"]
        expiration = cells[1].get_text(strip=True)
        usage = cells[2].get_text(strip=True)

        roles = ["Gateway", "Participant", "Endpoint"]
        for i in range(3):  # Gateway, Participants, Endpoint
            peers_html = cells[3 + i]
            for span in peers_html.find_all("span", class_="tunnel_peer"):
                country = "Unknown"
                node_id = "Unknown"
                abbrev = "Unknown"
                ip = "Unknown"

                img = span.find("img")
                if img:
                    country = img.get("title", "Unknown")
                tt = span.find("tt")
                if tt:
                    a_tag = tt.find("a")
                    if a_tag and "netdb?r=" in a_tag.get("href", ""):
                        node_id = a_tag["href"].split("netdb?r=")[-1]
                        abbrev = a_tag.get_text(strip=True)
                        ip = get_node_ip(node_id)
                    elif "Local" in tt.text:
                        node_id = "Local"
                        abbrev = "Local"
                        ip = "127.0.0.1"
                        country = "Localhost"

                row_id = f"{now}-{direction}-{node_id}-{roles[i]}"
                if row_id not in seen:
                    seen.add(row_id)
                    with open(OUTPUT_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            now, direction, expiration, usage,
                            roles[i], abbrev, node_id, country, ip
                        ])
    print(f"[{now}] Capture complete for this round.")
    time.sleep(FETCH_INTERVAL)

print("[DONE] 24-hour collection complete.")

