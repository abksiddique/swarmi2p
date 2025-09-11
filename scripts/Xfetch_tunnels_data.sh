#!/bin/bash

# Base URL of the I2P routers
BASE_URL="http://107.173.236.210"

# List of port numbers for each I2P router container
PORTS=(32995 32929 32885 33017 32984 33028 32841 32808 33039 33050 32896 33061 32918 32962 32797 33072 32951 32874 32830 32852)

# Persistent file paths
OUTPUT_DIR="/i2p_data"
mkdir -p "$OUTPUT_DIR"

# Function to fetch tunnels data from each I2P router
fetch_tunnels_data() {
    local PORT=$1
    TUNNELS_URL="$BASE_URL:$PORT/tunnels"
    TUNNELS_FILE="$OUTPUT_DIR/tunnels_data_$PORT.html"

    # Fetch the tunnels data
    curl -s "$TUNNELS_URL" -o "$TUNNELS_FILE"
}

# Function to parse and extract Exploratory tunnels
parse_exploratory_tunnels() {
    local PORT=$1
    TUNNELS_FILE="$OUTPUT_DIR/tunnels_data_$PORT.html"
    EXPLORATORY_FILE="$OUTPUT_DIR/exploratory_tunnels_$PORT.txt"

    # Extract the lines containing Exploratory tunnels and then parse them
    grep -A 1000 'Exploratory tunnels' "$TUNNELS_FILE" | grep -B 1000 'Client tunnels for shared clients' | grep -oP '(?<=href="netdb\?r=)[^"]+' > "$EXPLORATORY_FILE"
}

# Function to parse and extract Client tunnels for shared clients
parse_client_tunnels() {
    local PORT=$1
    TUNNELS_FILE="$OUTPUT_DIR/tunnels_data_$PORT.html"
    CLIENT_FILE="$OUTPUT_DIR/client_tunnels_$PORT.txt"

    # Extract the lines containing Client tunnels for shared clients and then parse them
    grep -A 1000 'Client tunnels for shared clients' "$TUNNELS_FILE" | grep -B 1000 '</table>' | grep -oP '(?<=href="netdb\?r=)[^"]+' > "$CLIENT_FILE"
}

# Function to display the parsed data for all routers
display_parsed_data() {
    for PORT in "${PORTS[@]}"; do
        EXPLORATORY_FILE="$OUTPUT_DIR/exploratory_tunnels_$PORT.txt"
        CLIENT_FILE="$OUTPUT_DIR/client_tunnels_$PORT.txt"
        
        echo "Exploratory Tunnels for Port $PORT (updated):"
        cat "$EXPLORATORY_FILE"
        
        echo "Client Tunnels for Shared Clients for Port $PORT (updated):"
        cat "$CLIENT_FILE"
    done
}

# Infinite loop to continuously collect and parse tunnels data from all routers
while true; do
    # Fetch and process data for all routers concurrently
    for PORT in "${PORTS[@]}"; do
        fetch_tunnels_data "$PORT" &
    done
    
    # Wait for all background processes to finish
    wait
    
    # Parse the fetched data
    for PORT in "${PORTS[@]}"; do
        parse_exploratory_tunnels "$PORT"
        parse_client_tunnels "$PORT"
    done
    
    # Display the results
    display_parsed_data
    
    # Wait for 1 second before the next iteration
    sleep 1
done
