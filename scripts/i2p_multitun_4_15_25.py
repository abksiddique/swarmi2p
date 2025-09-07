#!/bin/bash

# Configuration
OUTPUT_FILE="i2p_tunnel_data_detailed.csv"
LOG_FILE="i2p_tunnel_scraper_detailed.log"
I2P_TUNNELS_URL="http://127.0.0.1:7657/tunnels"
I2P_NETDB_URL="http://127.0.0.1:7657/netdb?r="
NETDB_DIR="$HOME/.i2p/netDb/"

# Write CSV Header
echo "Timestamp,Router (Full Node ID),Country,IP Address,Tunnels,Usage" > "$OUTPUT_FILE"

# Function to map Short Router ID to Full Node ID
map_short_to_full_id() {
    local short_id=$1
    local full_id=""
    match_file=$(ls "$NETDB_DIR"/routerInfo-"$short_id"* 2>/dev/null | head -n1)
    if [[ -n "$match_file" ]]; then
        full_id=$(basename "$match_file" | sed 's/routerInfo-//; s/.dat//')
    fi
    if [[ -z "$full_id" ]]; then
        echo "[WARNING] Could not find full Node ID for '$short_id'" >> "$LOG_FILE"
        full_id="$short_id"
    fi
    echo "$full_id"
}

# Function to extract IP address from NetDB page
get_ip_address() {
    local full_id=$1
    netdb_page=$(curl -s "${I2P_NETDB_URL}${full_id}")
    ip=$(echo "$netdb_page" | grep -oP 'host:\s*\K[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
    echo "${ip:-Unknown}"
}

# Function to extract country code from the flag next to router ID
get_country_code() {
    local router_html="$1"
    echo "$router_html" | grep -oP 'alt="\K[A-Z]{2}(?=")' | head -n1
}

# Function to extract tunnel data
extract_data() {
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    page_content=$(curl -s "$I2P_TUNNELS_URL")

    if [[ -z "$page_content" ]]; then
        echo "$timestamp [ERROR] Failed to fetch page content" >> "$LOG_FILE"
        return
    fi

    # Extract "Peers in multiple participating tunnels" section
    section_html=$(echo "$page_content" | sed -n '/Peers in multiple participating tunnels (including inactive)/,/Bandwidth Tiers/p')

    # Extract each table row
    echo "$section_html" | grep -oP '<tr>.*?</tr>' | while read -r row; do
        # Skip header row
        [[ "$row" == *"Router"* && "$row" == *"Tunnels"* ]] && continue

        # Extract Short Router ID
        short_id=$(echo "$row" | grep -oP '/netdb\?r=\K[^"]+')

        [[ -z "$short_id" ]] && continue

        # Get country code
        country=$(get_country_code "$row")

        # Get full router ID
        full_id=$(map_short_to_full_id "$short_id")

        # Get IP address
        ip_addr=$(get_ip_address "$full_id")

        # Get tunnels and usage columns (strip HTML, collapse spaces)
        cleaned_row=$(echo "$row" | sed 's/<[^>]*>//g' | tr -s ' ')
        tunnels=$(echo "$cleaned_row" | awk '{print $2}')
        usage=$(echo "$cleaned_row" | awk '{print substr($0, index($0,$3))}')

        echo "$timestamp,$full_id,$country,$ip_addr,$tunnels,$usage" >> "$OUTPUT_FILE"
    done
}

# Run the script every minute for 10 minutes
for ((i = 1; i <= 10; i++)); do
    extract_data
    sleep 60
done

echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Completed 10-minute detailed capture." >> "$LOG_FILE"

