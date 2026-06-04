# HomeWatch

A home network security monitor built as a learning project covering IT, cybersecurity, and Python development fundamentals.

## What It Does

- Scans any target on your local network for open ports and services
- Displays results in a clean web dashboard
- Stores scan history in SQLite
- Highlights new ports detected since the last scan as change alerts

## Architecture

```
[Monitor machine]                  [Target machine]
 Flask dashboard        <-LAN->     SSH server (port 22)
 Python scanner                     HTTP services
 SQLite history                     UFW firewall
```

## Scanned Ports

HomeWatch targets a curated set of ports relevant to a personal home lab:

| Port | Service |
|------|---------|
| 22 | SSH |
| 80 | HTTP |
| 135 | RPC |
| 443 | HTTPS |
| 445 | SMB |
| 3000 | Dev servers |
| 3389 | RDP (Remote Desktop) |
| 5000 / 5001 | Flask apps |
| 8080 / 8443 | Alternate HTTP/HTTPS |
| 11434 | Ollama (local AI) |
| 27036 | Steam Remote Play |

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
git clone https://github.com/sergioacosta-dev/homewatch.git
cd homewatch
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5001` in your browser.

### Scanning a target

Enter any local IP address in the dashboard and click **Scan Now**. To scan the machine running HomeWatch itself, enter `127.0.0.1`.

## What I Learned

- **IT:** IP addressing, SSH configuration, static networking, firewall rules (UFW)
- **Cybersecurity:** Port scanning, service enumeration, attack surface monitoring, change detection
- **Development:** Python scripting, Flask web apps, SQLite, Git workflow, project documentation

## Screenshot

<img width="1533" height="311" alt="Screenshot 2026-04-19 173847" src="https://github.com/user-attachments/assets/93db944d-c75b-4f8b-a1eb-c4ab3eacde52" />
