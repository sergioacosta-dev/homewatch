# HomeWatch

A home network security monitor built as a learning project covering IT, cybersecurity, and Python development fundamentals.

## What It Does

- Scans a target machine on your local network for open ports and services
- Displays results in a clean web dashboard
- Stores scan history in SQLite
- Alerts when new ports appear since the last scan

## Architecture

```
[Windows 11 PC]                    [Dell Linux Laptop]
 Flask dashboard        <-LAN->     SSH server (port 22)
 Python scanner                     HTTP server (port 8080)
 SQLite history                     UFW firewall
```

## Tech Stack

- Python 3
- Flask (web framework)
- python-nmap (network scanning)
- SQLite (scan history)
- nmap (system scanning tool)

## Setup

### Prerequisites

- Python 3.8+
- nmap installed ([nmap.org](https://nmap.org/download.html))

### Install

```bash
git clone https://github.com/YOURUSERNAME/homewatch.git
cd homewatch
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` in your browser.

## What I Learned

- **IT:** IP addressing, SSH configuration, static networking, firewall rules (UFW)
- **Cybersecurity:** Port scanning, service enumeration, attack surface monitoring, change detection
- **Development:** Python scripting, Flask web apps, SQLite, Git workflow, project documentation
