#!/bin/bash

echo "🔹 Step 1: Checking user permissions..."
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as a regular user, not root."
    exit 1
fi

USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)
SERVICE_FILE="/etc/systemd/system/i2p@$USER.service"
LOG_FILE="/var/log/i2p_setup.log"

# Redirect output to a log file for debugging
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🔹 Step 2: Verifying I2P installation..."
if [ ! -f "$HOME_DIR/i2p/i2prouter" ]; then
    echo "❌ I2P is not installed in $HOME_DIR/i2p. Please install it first."
    exit 1
fi

echo "✅ I2P found! Proceeding with setup..."

# Create systemd service file dynamically
echo "🔹 Step 3: Creating systemd service for I2P..."
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=I2P Router for $USER
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$HOME_DIR/i2p/i2prouter start
ExecStop=$HOME_DIR/i2p/i2prouter stop
Restart=always
WorkingDirectory=$HOME_DIR/i2p
Environment=HOME=$HOME_DIR
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created!"

echo "🔹 Step 4: Setting up systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable i2p@$USER
echo "✅ I2P is now set to start on every reboot!"

echo "🔹 Step 5: Starting I2P now..."
sudo systemctl start i2p@$USER
systemctl status i2p@$USER --no-pager

echo "✅ I2P is running in the background!"

# Ask user before rebooting
echo "🔹 Final Step: A reboot is required to complete the setup."
read -p "Do you want to reboot now? (y/N): " REBOOT_CONFIRM
if [[ "$REBOOT_CONFIRM" =~ ^[Yy]$ ]]; then
    echo "🔄 Rebooting now..."
    sudo reboot
else
    echo "✅ Setup complete! Please reboot manually when you're ready."
fi

