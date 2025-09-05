# WNRIPS

**Windows Name Resolution Is Plain S\*\*t**  
A Flask-based dashboard that runs `nbtscan` every 5 minutes and displays NetBIOS scan results in a sortable, searchable web interface.

## Setup Instructions

### 1. Clone the Project

    git clone
    cd wnrips

### 2. Create and Activate Virtual Environment

    python3 -m venv venv

### 3. Install Python Dependencies

    pip install flask apscheduler waitress

### 4. Install nbtscan

    sudo apt update
    sudo apt install nbtscan

## Allow Passwordless nbtscan

To allow the app to run `nbtscan` without prompting for a password, add this line to your sudoers file:

    sudo visudo

Then add:

    yourusername ALL=(ALL) NOPASSWD: /usr/bin/nbtscan

Replace `yourusername` with your actual Linux username.

## Usage

`venv/bin/python WNDIPS.py ip_range`

where `ip_range` is in CIDR notation (e.g. 10.0.7.0/24)

## systemd Service Setup

Create a systemd service to run WNRIPS on boot.

### 1. Create the service file

    sudo nano /etc/systemd/system/wnrips.service

Paste the following:

    [Unit]
    Description=WNRIPS Flask App with venv
    After=network.target

    [Service]
    User=yourusername
    WorkingDirectory=/home/yourusername/wndips
    ExecStart=/home/yourusername/wnrips/venv/bin/python WNDIPS.py ip_range
    Restart=always
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target

Replace `yourusername` with your actual username, adjust paths and set ip_range.

### 2. Enable and Start the Service

    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable wnrips.service
    sudo systemctl start wnrips.service

### 3. Check Status

    sudo systemctl status wnrips.service

## Access the Web Interface

Once running, open your browser and go to:

    http://localhost:5000

Or use your server’s IP if running remotely.

## Features

- Runs `nbtscan -r ip_range` every 5 minutes
- Displays results in a sortable, searchable table
- Search bar and pagination included
- Auto-starts on boot via systemd

## Credits
 
Inspired by the eternal mystery of why the results of windows network discovery are completely random.
