#!/bin/bash

# Determine the current user and home directory
USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)
I2P_DIR="$HOME_DIR/i2p"
CRON_FILE="/tmp/i2p_cron"

# Check if the I2P directory exists
if [ ! -d "$I2P_DIR" ]; then
    echo "I2P directory not found at $I2P_DIR. Please ensure I2P is installed in the home directory."
    exit 1
fi

# Create a temporary cron file
echo "Creating cron job for I2P..."
echo "@reboot $I2P_DIR/i2prouter start" > $CRON_FILE

# Install the cron job
crontab $CRON_FILE
rm $CRON_FILE

echo "Cron job created! I2P will start automatically on reboot."

# Start I2P immediately
echo "Starting I2P now..."
$I2P_DIR/i2prouter start

echo "Setup complete! I2P is running and will start automatically on reboot."
