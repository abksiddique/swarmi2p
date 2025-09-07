#!/bin/bash

# Set log directory
LOG_DIR="$HOME/i2p_peers_logs"
mkdir -p "$LOG_DIR"

# Define log files
PEERS_LOG="$LOG_DIR/i2p_peers.log"
UNIQUE_COUNT_LOG="$LOG_DIR/unique_peers_count.log"
ERROR_LOG="$LOG_DIR/errors.log"

# Temporary file for tracking unique peers
TMP_UNIQUE="$LOG_DIR/tmp_unique.txt"
touch "$TMP_UNIQUE"

# Base URL
BASE_URL="http://127.0.0.1:7657/netdb?f=1&ps=500"

# Set script runtime (24 hours)
START_TIME=$(date +%s)
END_TIME=$((START_TIME + 86400))

# Function to fetch peers
capture_peers() {
    while [ "$(date +%s)" -lt "$END_TIME" ]; do
        echo "$(date): Fetching peers..." >> "$ERROR_LOG"

        PAGE=1
        while true; do
            URL="${BASE_URL}&pg=${PAGE}"
            PAGE_CONTENT=$(curl -s "$URL")

            # Check if page has no content
            if [[ -z "$PAGE_CONTENT" || "$PAGE_CONTENT" == *"No routers found"* ]]; then
                echo "$(date): No more pages to fetch." >> "$ERROR_LOG"
                break
            fi

            # Extract Node ID, IP Address, Port, and Capabilities
            echo "$PAGE_CONTENT" | awk '
                /Router:/ { node_id=$2 }
                /NTCP2:/ { ip=$(NF-3); port=$(NF-1) }
                /SSU2:/ { ip=$(NF-3); port=$(NF-1) }
                /caps =/ { caps=$3 }
                node_id && ip && port { print node_id, ip, port, caps; node_id=""; ip=""; port=""; caps="" }
            ' >> "$PEERS_LOG"

            PAGE=$((PAGE + 1))
        done

        # Track unique peers
        sort "$PEERS_LOG" | uniq > "$TMP_UNIQUE"
        echo "Total unique peers found: $(wc -l < "$TMP_UNIQUE")" > "$UNIQUE_COUNT_LOG"

        # Sleep before fetching again
        sleep 60
    done
}

# Run in background
nohup bash -c "capture_peers" > "$LOG_DIR/script_output.log" 2>&1 &

# Store the PID
echo $! > "$LOG_DIR/capture_peers.pid"
echo "Script is running in the background. PID: $(cat $LOG_DIR/capture_peers.pid)"
