#!/bin/bash

# Knowledge Hub - Monitoring Agent Installation Script
# This script automates the setup of the monitoring client on a Linux host.

set -e # Exit immediately if a command exits with a non-zero status

# 1. Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root or with sudo."
   exit 1
fi

echo "Starting Monitoring Agent installation..."

# Define paths
INSTALL_DIR=$(pwd)
VENV_DIR="$INSTALL_DIR/venv"
LOG_FILE="/var/log/monitor_agent.log"
CRON_JOB="* * * * * cd $INSTALL_DIR && $VENV_DIR/bin/python3 $INSTALL_DIR/monitor.py >> $LOG_FILE 2>&1"

# 2. Check and install Python3 and pip
echo "Checking system dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    apt-get update && apt-get install -y python3
else
    echo "Python3 is already installed."
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing..."
    apt-get update && apt-get install -y python3-pip
else
    echo "pip3 is already installed."
fi

# Ensure python3-venv is installed (needed for virtual environments on Debian/Ubuntu)
if ! dpkg -l | grep -q python3-venv; then
    echo "Installing python3-venv..."
    apt-get update && apt-get install -y python3-venv
fi

# 3. Setup Virtual Environment and Install Dependencies
echo "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created at $VENV_DIR."
else
    echo "Virtual environment already exists."
fi

echo "Installing requirements from requirements.txt..."
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    echo "Dependencies installed successfully."
else
    echo "ERROR: requirements.txt not found in $INSTALL_DIR!"
    exit 1
fi

# 4. Check for .env file
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "WARNING: .env file not found."
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
        echo "Created .env from .env.example. PLEASE UPDATE IT with your API credentials."
    else
        echo "Please create a .env file with MONITOR_API_URL and MONITOR_API_KEY."
    fi
else
    echo ".env file found."
fi

# 5. Setup Cron Job
echo "Setting up cron job..."
# Check if the job already exists to avoid duplicates (ignoring error if crontab is empty)
if crontab -l 2>/dev/null | grep -q "$INSTALL_DIR/monitor.py"; then
    echo "Cron job already exists for this script."
else
    # Append the new cron job to the existing crontab
    # We use '|| true' because if there's no crontab, 'crontab -l' returns exit code 1,
    # which would normally crash the script due to 'set -e' at the top of the file.
    (crontab -l 2>/dev/null || true; echo "$CRON_JOB") | crontab -
    echo "Cron job added. The script will run every minute."
fi

echo "Creating log file at $LOG_FILE..."
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"

echo ""
echo "Installation complete!"
echo "The monitoring agent is now scheduled to run every minute."
echo "You can check the logs anytime by running: tail -f $LOG_FILE"
