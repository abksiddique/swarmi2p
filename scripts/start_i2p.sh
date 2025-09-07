#!/bin/bash

# Determine the current user and home directory
USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)
I2P_DIR="$HOME_DIR/i2p"
SERVICE_FILE="/etc/systemd/system/i2p.service"

# Check if the I2P directory exists
if [ ! -d "$I2P_DIR" ]; then
    echo "I2P directory not found at $I2P_DIR. Please ensure I2P is installed in the home directory."
    exit 1
fi

# Create systemd service file
echo "Creating systemd service for I2P..."
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=I2P Router Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$I2P_DIR/i2prouter start
ExecStop=$I2P_DIR/i2prouter stop
Restart=on-failure
WorkingDirectory=$I2P_DIR
Environment=HOME=$HOME_DIR
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created!"

# Reload systemd daemon, enable and start the service
echo "Setting up systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable i2p.service
sudo systemctl start i2p.service

# Check the status of the service
echo "Checking the status of the I2P service..."
systemctl status i2p.service --no-pager

echo "Setup complete! I2P is now set to start on every reboot."
