#!/bin/bash

# Base URL of the I2P routers
BASE_URL="http://107.173.236.210"

# List of port numbers for each I2P router container
PORTS=(32995 32929 32885 33017 32984 33028 32841 32808 33039 33050 32896 33061 32918 32962 32797 33072 32951 32874 32830 32852)

# File paths
OUTPUT_DIR="/i2p_data1"
HIGH_CAPACITY_FILE="$OUTPUT_DIR/high_capacity_routers.txt"
FREQUENCY_FILE="$OUTPUT_DIR/high_capacity_in_client_comm_freq.txt"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Clear the frequency file at the start
> "$FREQUENCY_FILE"

# Function to fetch and process client tunnels from each I2P router
fetch_and_process_client_tunnels() {
    local PORT=$1
    TUNNELS_URL="$BASE_URL:$PORT/tunnels"
    TUNNELS_FILE="$OUTPUT_DIR/tunnels_data_$PORT.html"
    CLIENT_FILE="$OUTPUT_DIR/client_tunnels_$PORT.txt"

    # Fetch the tunnels data
    curl -s "$TUNNELS_URL" -o "$TUNNELS_FILE"

    # Extract and save Client tunnels for shared clients
    grep -A 1000 'Client tunnels for shared clients' "$TUNNELS_FILE" | grep -B 1000 '</table>' | grep -oP '(?<=href="netdb\?r=)[^"]+' > "$CLIENT_FILE"
}

# Function to count the frequency of high-capacity routers in Client Communication tunnels
count_high_capacity_in_client_comm() {
    for PORT in "${PORTS[@]}"; do
        CLIENT_FILE="$OUTPUT_DIR/client_tunnels_$PORT.txt"
        while read -r router_id; do
            count=$(grep -o "$router_id" "$CLIENT_FILE" | wc -l)
            echo "$router_id: $count" >> "$FREQUENCY_FILE"
        done < "$HIGH_CAPACITY_FILE"
    done
}

# Infinite loop to continuously collect and process tunnels data
while true; do
    # Fetch and process client tunnels for all routers
    for PORT in "${PORTS[@]}"; do
        fetch_and_process_client_tunnels "$PORT" &
    done
    
    # Wait for all background processes to finish
    wait
    
    # Count the frequency of high-capacity routers in the client tunnels
    count_high_capacity_in_client_comm
    
    # Display the results
    echo "Frequency of High-Capacity Routers in Client Communication Tunnels:"
    cat "$FREQUENCY_FILE"
    
    # Wait for 1 second before the next iteration
    sleep 1
done
