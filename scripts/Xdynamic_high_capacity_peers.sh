#!/bin/bash

# Base URL of the I2P routers
BASE_URL="http://107.173.236.210"

# File paths
OUTPUT_DIR="/i2p_data2"
PEERS_FILE="$OUTPUT_DIR/high_capacity_peers.txt"
FREQUENCY_FILE="$OUTPUT_DIR/peer_frequency.txt"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Clear the peers file at the start
> "$PEERS_FILE"

# Function to fetch high-capacity nodes from each I2P router
fetch_high_capacity_nodes() {
    local PORT=$1
    I2P_URL="$BASE_URL:$PORT/profiles"
    OUTPUT_FILE="$OUTPUT_DIR/high_capacity_routers_$PORT.html"
    
    # Fetch the high-capacity nodes
    curl -s "$I2P_URL" -o "$OUTPUT_FILE"
    
    # Parse and extract high-capacity peers
    grep -A 1000 'High Capacity' "$OUTPUT_FILE" | grep -B 1000 '</table>' | grep -oP '(?<=href="netdb\?r=)[^"]+' >> "$PEERS_FILE"
}

# Function to count the frequency of each peer
count_peer_frequency() {
    sort "$PEERS_FILE" | uniq -c | sort -nr > "$FREQUENCY_FILE"
}

# Function to discover currently active ports mapped to I2P services
discover_ports() {
    # Find all active ports on the host that map to port 7657 inside the containers
    docker ps --format '{{.ID}}' | while read container_id; do
        docker port "$container_id" | grep '7657/tcp' | awk -F'[:]' '{print $2}'
    done
}

# Infinite loop to continuously discover ports and collect data
while true; do
    # Clear the peers file before each collection
    > "$PEERS_FILE"
    
    # Discover the active ports dynamically
    PORTS=$(discover_ports)

    # Fetch the high-capacity nodes from all discovered routers concurrently
    for PORT in $PORTS; do
        fetch_high_capacity_nodes "$PORT" &
    done
    
    # Wait for all background processes to finish
    wait
    
    # Count the frequency of each peer
    count_peer_frequency
    
    # Output the result
    echo "Peer ID frequencies (updated):"
    cat "$FREQUENCY_FILE"
    
    # Wait for 1 second before the next iteration
    sleep 1
done
