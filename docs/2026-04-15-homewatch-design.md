# HomeWatch — Design Spec
**Date:** 2026-04-15
**Status:** Approved

---

## Overview

HomeWatch is a two-machine home lab project that teaches IT, cybersecurity, and development fundamentals through building a real network security monitor. The Linux laptop acts as a server/target; the Windows 11 PC runs a Python dashboard that scans the local network, detects open ports, and alerts on unexpected changes.

---

## Architecture

```
[Windows 11 PC]                    [Dell Linux Laptop - Omarchy]
 Flask dashboard        <--LAN-->   SSH server
 Python scanner                     Static local IP
 SQLite history                     Services running (SSH, HTTP)
 Browser UI                         UFW firewall configured
```

Both machines on home WiFi. No cloud services, no external dependencies.

---

## Phases

### Phase 1 — Lab Setup (2–3 weeks)
**Skills: IT / Linux / Networking**

- Enable and harden SSH on the Linux laptop
- Assign static local IPs to both machines (or use DHCP reservations on router)
- Learn core Linux commands: `ping`, `ifconfig`/`ip a`, `netstat`, `ss`, `ufw`
- Confirm SSH connection from Windows to Linux via terminal
- Deliverable: can SSH from Windows PC into Linux laptop reliably

### Phase 2 — Network Scanner (2–3 weeks)
**Skills: Cybersecurity / Python**

- Install `nmap` on Linux; run manual scans to understand output
- Write a Python script (`scanner.py`) that:
  - Accepts an IP range as input
  - Uses `python-nmap` to scan for open ports and services
  - Outputs results as structured JSON
- Learn what common ports mean (22, 80, 443, 3306, 5432, etc.)
- Deliverable: `scanner.py` that produces a JSON report of open ports on the network

### Phase 3 — Flask Dashboard (3–4 weeks)
**Skills: Python / Web Development / Database**

- Build a Flask web app (`app.py`) on the Windows PC that:
  - Triggers a scan on demand (button in the UI)
  - Displays current open ports and services in a clean table
  - Stores each scan result in SQLite with a timestamp
  - Shows scan history (last 10 runs) so changes over time are visible
  - Highlights any port that wasn't open in the previous scan (simple alert)
- HTML/CSS dashboard — no JavaScript frameworks needed
- Deliverable: running web app accessible at `http://localhost:5000`

### Phase 4 — Portfolio (1 week)
**Skills: Git / Documentation**

- Initialize a Git repo in the project folder
- Push to GitHub (public repo)
- Write a `README.md` that includes:
  - What the project does
  - Architecture diagram (ASCII is fine)
  - Setup instructions
  - Screenshots of the dashboard
  - What you learned
- Deliverable: public GitHub repo with working README

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Scanner + Flask app |
| nmap + python-nmap | Network scanning |
| Flask | Web framework |
| SQLite + sqlite3 | Scan history storage |
| HTML/CSS | Dashboard UI |
| Git + GitHub | Version control + portfolio |
| SSH | Machine-to-machine access |
| UFW | Linux firewall (Phase 1) |

---

## File Structure (target end state)

```
homewatch/
  scanner.py          # network scanner script
  app.py              # Flask web app
  db.py               # SQLite helpers
  templates/
    index.html        # dashboard UI
  static/
    style.css
  homewatch.db        # SQLite database (gitignored)
  requirements.txt    # Python dependencies
  README.md
  .gitignore
```

---

## Success Criteria

- [x] Can SSH from Windows PC into Linux laptop
- [x] `scanner.py` returns accurate open port data as JSON
- [x] Flask dashboard runs locally and displays scan results
- [x] Scan history is stored and past scans are visible
- [x] Unexpected new ports are highlighted in the UI
- [x] Public GitHub repo with a clear README and screenshots

---

## What You'll Know After This Project

**IT:** IP addressing, static IPs, SSH, network services, firewall rules
**Cybersecurity:** Port scanning, service enumeration, attack surface awareness, change detection
**Development:** Python scripting, Flask web apps, SQLite, Git workflow, project documentation
