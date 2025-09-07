#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I2P Participating Tunnels Data Extraction Script - Continuous Mode for 24h
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import csv
from datetime import datetime
import re

# === Configuration ===
URL = "http://127.0.0.1:7657/tunnels"
FETCH_INTERVAL = 10  # seconds between fetches

# Set new output folder and file name
user_home = os.path.expanduser("~")
OUTPUT_DIR = os.path.join(user_home, "i2p_tunnel_data_4_18_25")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "i2p_tunnel_data_4_18_25.csv")

csv_headers = [
    "Timestamp",
    "Receive on",
    "From Full ID",
    "From Country",
    "From Abbrev",
    "From IP",
    "Send on",
    "To Full ID",
    "To Country",
    "To Abbrev",
    "To IP",
    "Expiration",
    "Usage",
    "Rate",
    "Role"
]

if not os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

peer_cache = {}

def get_node_ip(node_id):
    detail_url = "http://127.0.0.1:7657/netdb?r=" + node_id
    if node_id in peer_cache:
        return peer_cache[node_id]
    try:
        response = requests.get(detail_url, timeout=5)
        html = re.sub(r'<[^>]+>', ' ', response.text)
        ipv4 = re.findall(r'(?i)host:\s*((?:\d{1,3}\.){3}\d{1,3})', html)
        ipv6 = re.findall(r'(?i)host:\s*((?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4})', html)
        ip_list = list(dict.fromkeys(ipv4 + ipv6))
        result = ";".join(ip_list) if ip_list else "Unknown"
    except Exception as e:
        print(f"Error fetching detail for node {node_id}: {e}")
        result = "Error"
    peer_cache[node_id] = result
    return result

def extract_peer_from_cell(cell):
    cell_text = cell.get_text(strip=True)
    if "Local" in cell_text:
        return ("Local", "Local")
    a_tag = cell.find("a")
    if a_tag and "netdb?r=" in a_tag.get("href", ""):
        full_id = a_tag["href"].split("netdb?r=")[-1]
        abbrev = a_tag.get_text(strip=True)
        return (full_id, abbrev)
    tt_tag = cell.find("tt")
    if tt_tag:
        text = tt_tag.get_text(strip=True)
        return (text, text)
    return ("Unknown", "Unknown")

def extract_tunnel_data(html):
    soup = BeautifulSoup(html, "html5lib")
    header = soup.find("h3", id="participating")
    if not header:
        print("Participating tunnels section not found.")
        return []
    table = header.find_next("table", class_="tunneldisplay tunnels_participating")
    if not table:
        print("Participating tunnels table not found.")
        return []
    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        receive_on = cells[0].get_text(strip=True)
        from_cell = cells[1]
        from_img = from_cell.find("img")
        from_country = from_img["title"] if from_img and "title" in from_img.attrs else "Unknown"
        from_full, from_abbrev = extract_peer_from_cell(from_cell)
        from_ip = get_node_ip(from_full) if from_full not in ("Unknown", "Error") else "Unknown"
        send_on = cells[2].get_text(strip=True)
        to_cell = cells[3]
        to_img = to_cell.find("img")
        to_country = to_img["title"] if to_img and "title" in to_img.attrs else "Unknown"
        to_full, to_abbrev = extract_peer_from_cell(to_cell)
        to_ip = get_node_ip(to_full) if to_full not in ("Unknown", "Error") else "Unknown"
        expiration = cells[4].get_text(strip=True)
        usage = cells[5].get_text(strip=True)
        rate = cells[6].get_text(strip=True)
        role = cells[7].get_text(strip=True)
        data.append((
            receive_on,
            from_full, from_country, from_abbrev, from_ip,
            send_on,
            to_full, to_country, to_abbrev, to_ip,
            expiration, usage, rate, role
        ))
    return data

# === Continuous Capture Loop ===
print(f"Started continuous capture. Saving to: {OUTPUT_FILE}")
while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()
        html = response.text
        extracted = extract_tunnel_data(html)
        if extracted:
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for record in extracted:
                    writer.writerow([current_time] + list(record))
            print(f"[{current_time}] Captured {len(extracted)} records.")
        else:
            print(f"[{current_time}] No data found.")
    except Exception as e:
        print(f"[{current_time}] Error: {e}")
    time.sleep(FETCH_INTERVAL)

