#!/bin/bash

# Base URL of the I2P routers
BASE_URL="http://107.173.236.210"

# File paths
OUTPUT_DIR="/i2p_data3"
ALL_PEERS_FILE="$OUTPUT_DIR/all_peers.txt"
TUNNEL_PEERS_FILE="$OUTPUT_DIR/tunnel_peers.txt"
HIGH_CAPACITY_CANDIDATES="$OUTPUT_DIR/high_capacity_candidates.txt"
FREQUENCY_FILE="$OUTPUT_DIR/high_capacity_frequency.txt"
HIGH_CAPACITY_FILE="$OUTPUT_DIR/high_capacity_routers.txt"  # File to store the 30 high-capacity routers

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Clear temporary files at the start
> "$ALL_PEERS_FILE"
> "$TUNNEL_PEERS_FILE"
> "$HIGH_CAPACITY_CANDIDATES"

# Initialize or verify the frequency file exists
if [ ! -f "$FREQUENCY_FILE" ]; then
    touch "$FREQUENCY_FILE"
fi

# Function to fetch all peers from each I2P router
fetch_all_peers() {
    local PORT=$1
    I2P_URL="$BASE_URL:$PORT/profiles?f=1"
    OUTPUT_FILE="$OUTPUT_DIR/all_peers_$PORT.html"
    
    # Fetch all peers
    curl -s "$I2P_URL" -o "$OUTPUT_FILE"
    
    # Extract all peers
    grep -oP '(?<=href="netdb\?r=)[^"]+' "$OUTPUT_FILE" >> "$ALL_PEERS_FILE"
}

# Function to identify the top 30 high-capacity peers from all peers
identify_high_capacity_nodes() {
    # Clear the high-capacity file before starting
    > "$HIGH_CAPACITY_FILE"

    # Find the top 30 most frequent peers in the all peers file and save them as high-capacity nodes
    sort "$ALL_PEERS_FILE" | uniq -c | sort -nr | head -n 30 | awk '{print $2}' > "$HIGH_CAPACITY_FILE"
}

# Function to fetch and record peers from tunnels (client and exploratory)
fetch_and_record_tunnel_peers() {
    local PORT=$1
    TUNNELS_URL="$BASE_URL:$PORT/tunnels"
    TUNNELS_FILE="$OUTPUT_DIR/tunnels_data_$PORT.html"
    
    # Fetch the tunnels data
    curl -s "$TUNNELS_URL" -o "$TUNNELS_FILE"
    
    # Record all peers in the client and exploratory tunnels
    grep -A 1000 'Exploratory tunnels' "$TUNNELS_FILE" | grep -B 1000 'Client tunnels for shared clients' | grep -oP '(?<=href="netdb\?r=)[^"]+' >> "$TUNNEL_PEERS_FILE"
    grep -A 1000 'Client tunnels for shared clients' "$TUNNELS_FILE" | grep -B 1000 '</table>' | grep -oP '(?<=href="netdb\?r=)[^"]+' >> "$TUNNEL_PEERS_FILE"
}

# Function to identify high-capacity candidates based on tunnel peers
identify_high_capacity_candidates() {
    # Clear the high-capacity candidates file before starting
    > "$HIGH_CAPACITY_CANDIDATES"

    # Compare tunnel peers with the top 30 high-capacity nodes
    while read -r peer; do
        if grep -q "$peer" "$HIGH_CAPACITY_FILE"; then
            echo "$peer" >> "$HIGH_CAPACITY_CANDIDATES"
        fi
    done < "$TUNNEL_PEERS_FILE"
}

# Function to update frequency counts
update_frequency_counts() {
    # Create a temporary file to store the updated frequencies
    TEMP_FREQUENCY_FILE=$(mktemp)

    # Read the existing frequencies into an associative array
    declare -A frequency_map
    while IFS=":" read -r router_id count; do
        frequency_map["$router_id"]=$count
    done < "$FREQUENCY_FILE"

    # Increment the frequency count for each high-capacity candidate
    while read -r candidate; do
        if [[ -n "${frequency_map[$candidate]}" ]]; then
            frequency_map["$candidate"]=$((frequency_map["$candidate"] + 1))
        else
            frequency_map["$candidate"]=1
        fi
    done < "$HIGH_CAPACITY_CANDIDATES"

    # Write the updated frequencies back to the temporary file
    for router_id in "${!frequency_map[@]}"; do
        echo "$router_id:${frequency_map[$router_id]}" >> "$TEMP_FREQUENCY_FILE"
    done

    # Replace the old frequency file with the updated one
    mv "$TEMP_FREQUENCY_FILE" "$FREQUENCY_FILE"
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
    # Clear the peers files before each collection
    > "$ALL_PEERS_FILE"
    > "$TUNNEL_PEERS_FILE"
    
    # Discover the active ports dynamically
    PORTS=$(discover_ports)

    # Fetch all peers and record tunnel peers from all discovered routers concurrently
    for PORT in $PORTS; do
        fetch_all_peers "$PORT" &
        fetch_and_record_tunnel_peers "$PORT" &
    done
    
    # Wait for all background processes to finish
    wait
    
    # Identify the top 30 high-capacity nodes from all peers
    identify_high_capacity_nodes
    
    # Identify high-capacity candidates based on tunnel peers and all peers
    identify_high_capacity_candidates
    
    # Update frequency counts for high-capacity candidates
    update_frequency_counts
    
    # Output the result
    echo "High-Capacity Peer ID frequencies (updated):"
    cat "$FREQUENCY_FILE"
    
    # Wait for 1 second before the next iteration
    sleep 1
done
