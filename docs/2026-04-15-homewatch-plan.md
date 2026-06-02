# HomeWatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a two-machine home lab with a Python dashboard that scans your local network, detects open ports, and alerts on changes — covering IT, cybersecurity, and development fundamentals.

**Architecture:** Linux laptop (Dell/Omarchy) acts as a server/target with SSH enabled and a firewall configured. Windows 11 PC runs a Python Flask web app that scans the network via nmap, stores results in SQLite, and displays a live dashboard with change alerts in the browser.

**Tech Stack:** Python 3, Flask, python-nmap, SQLite, HTML/CSS, nmap (system tool), SSH, UFW (Linux firewall), Git, GitHub

---

## File Structure

```
F:/IT_Proj/homewatch/
  scanner.py          # scans the network, returns JSON of open ports
  app.py              # Flask web app — routes, scan trigger, alert logic
  db.py               # SQLite helpers — save scan, get history
  templates/
    index.html        # dashboard UI
  static/
    style.css         # basic styling
  requirements.txt    # Python dependencies
  .gitignore          # excludes homewatch.db and __pycache__
  README.md           # portfolio documentation
```

---

## Phase 1 — Lab Setup (IT Skills)

**Goal:** Get both machines talking to each other over SSH. This is your IT foundation — understanding IPs, ports, and remote access.

---

### Task 1: Find Both Machine IPs

**What you're learning:** Every device on a network has a local IP address. You need to know these to target your scanner.

**On your Linux laptop (Dell/Omarchy):**

- [x] Open a terminal on the Linux laptop

- [x] Run:
```bash
ip a
```
Expected output: You'll see a block starting with `eth0` or `wlan0`. Look for a line like:
```
inet 192.168.1.XX/24
```
That number (e.g. `192.168.1.42`) is your Linux laptop's local IP. Write it down.

- [x] Also run to see your network range:
```bash
ip route
```
Look for a line like `192.168.1.0/24 dev wlan0` — that `/24` means your network covers `192.168.1.1` to `192.168.1.254`.

**On your Windows 11 PC:**

- [x] Press `Win + R`, type `cmd`, press Enter

- [x] Run:
```
ipconfig
```
Look for `IPv4 Address` under your WiFi adapter. Write it down (e.g. `192.168.1.55`).

- [x] Verify both machines can reach each other:
```
ping 192.168.1.42
```
(replace with your Linux laptop's IP)
Expected: you see replies, not timeouts. If you get timeouts, both machines must be on the same WiFi network.

---

### Task 2: Enable SSH on the Linux Laptop

**What you're learning:** SSH (Secure Shell) lets you control one computer from another over the network — the foundation of remote IT administration.

- [x] On the Linux laptop, install the SSH server:
```bash
sudo apt update && sudo apt install openssh-server -y
```
(If on Arch-based: `sudo pacman -S openssh`)

- [x] Start and enable SSH so it runs automatically on boot:
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

- [x] Verify SSH is running:
```bash
sudo systemctl status ssh
```
Expected: you see `Active: active (running)` in green.

- [x] Check which port SSH is listening on (default is 22):
```bash
ss -tlnp | grep ssh
```
Expected: `*:22` in the output.

- [x] Commit your understanding — write the following in a notes file `F:/IT_Proj/notes.txt`:
```
Linux IP: [your linux IP]
Windows IP: [your windows IP]
SSH port: 22
SSH command to connect: ssh [your linux username]@[your linux IP]
```

---

### Task 3: SSH from Windows into Linux

**What you're learning:** Connecting to a remote machine — the most fundamental IT skill.

- [x] On Windows, open PowerShell (search "PowerShell" in Start menu)

- [x] Connect to your Linux laptop:
```
ssh yourusername@192.168.1.42
```
Replace `yourusername` with your Linux account name and `192.168.1.42` with your Linux IP.

- [x] The first time you connect, you'll see:
```
The authenticity of host '192.168.1.42' can't be established.
Are you sure you want to continue? (yes/no)
```
Type `yes` and press Enter.

- [x] Enter your Linux password when prompted.

Expected: Your terminal prompt changes to show your Linux username and machine name. You are now inside the Linux laptop from your Windows PC.

- [x] Try a command to confirm:
```bash
whoami
```
Expected: prints your Linux username.

- [x] Type `exit` to disconnect.

---

### Task 4: Configure the Linux Firewall

**What you're learning:** Firewalls control which ports are open to the network — a core cybersecurity concept. You'll configure one, then later scan it from the outside.

- [x] On the Linux laptop, install UFW (Uncomplicated Firewall) if not present:
```bash
sudo apt install ufw -y
```

- [x] Allow SSH through the firewall (critical — do this BEFORE enabling UFW or you'll lock yourself out):
```bash
sudo ufw allow ssh
```

- [x] Enable the firewall:
```bash
sudo ufw enable
```
Type `y` when prompted.

- [x] Check the firewall status:
```bash
sudo ufw status verbose
```
Expected output:
```
Status: active
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
```

- [x] Also run a simple web server on port 8080 so your scanner has something interesting to find:
```bash
python3 -m http.server 8080 &
```
This starts a basic HTTP server in the background. Now your laptop has two open ports: 22 (SSH) and 8080 (HTTP).

- [x] Allow port 8080 through the firewall:
```bash
sudo ufw allow 8080
```

**Phase 1 complete.** You now have two networked machines, SSH access, and a configured firewall. That's real IT work.

---

## Phase 2 — Network Scanner (Cybersecurity Skills)

**Goal:** Write a Python script that scans your local network for open ports — the same technique used in real security assessments.

---

### Task 5: Set Up Python Environment on Windows

- [x] Open PowerShell on Windows and check Python is installed:
```
python --version
```
Expected: `Python 3.x.x`. If not found, download from python.org and install (check "Add to PATH").

- [x] Create the project folder:
```
mkdir F:\IT_Proj\homewatch
cd F:\IT_Proj\homewatch
```

- [x] Install required Python libraries:
```
pip install flask python-nmap
```
Expected: both packages install without errors.

- [x] Install nmap system tool on Windows:
  - Go to https://nmap.org/download.html
  - Download the Windows installer (.exe)
  - Run the installer — accept defaults
  - Restart PowerShell after installing

- [x] Verify nmap works:
```
nmap --version
```
Expected: `Nmap 7.x` version line.

- [x] Create `requirements.txt`:
```
flask
python-nmap
```
Save this file at `F:\IT_Proj\homewatch\requirements.txt`

---

### Task 6: Write the Network Scanner

**What you're learning:** nmap is the industry-standard network scanning tool used by IT admins and security professionals. python-nmap wraps it in Python.

- [x] Create `F:\IT_Proj\homewatch\scanner.py` with this content:

```python
import nmap
import json
from datetime import datetime


def scan_host(target_ip):
    """
    Scan a single host for open ports and running services.
    Returns a dict with host info and list of open ports.
    """
    nm = nmap.PortScanner()

    # -sV detects service versions, -T4 is fast, --open only shows open ports
    nm.scan(hosts=target_ip, arguments='-sV -T4 --open -p 1-1024')

    result = {
        'target': target_ip,
        'scanned_at': datetime.now().isoformat(),
        'status': 'unknown',
        'ports': []
    }

    if target_ip not in nm.all_hosts():
        result['status'] = 'unreachable'
        return result

    host = nm[target_ip]
    result['status'] = host.state()

    if 'tcp' in host:
        for port, data in host['tcp'].items():
            if data['state'] == 'open':
                result['ports'].append({
                    'port': port,
                    'protocol': 'tcp',
                    'service': data.get('name', 'unknown'),
                    'version': data.get('version', ''),
                    'state': data['state']
                })

    return result


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python scanner.py <ip_address>')
        print('Example: python scanner.py 192.168.1.42')
        sys.exit(1)

    target = sys.argv[1]
    print(f'Scanning {target}...')

    result = scan_host(target)
    print(json.dumps(result, indent=2))
```

- [x] Run the scanner against your Linux laptop (replace IP with yours):
```
python scanner.py 192.168.1.42
```
Expected output (similar to):
```json
{
  "target": "192.168.1.42",
  "scanned_at": "2026-04-15T20:00:00",
  "status": "up",
  "ports": [
    {
      "port": 22,
      "protocol": "tcp",
      "service": "ssh",
      "version": "OpenSSH 8.x",
      "state": "open"
    },
    {
      "port": 8080,
      "protocol": "tcp",
      "service": "http",
      "version": "",
      "state": "open"
    }
  ]
}
```

If you see ports 22 and 8080 listed — your scanner works. This is exactly what a security professional does when assessing a network.

- [x] Try scanning a port that should be closed. On your Linux laptop, block port 8080 temporarily:
```bash
sudo ufw deny 8080
```
Then re-run the scanner. Port 8080 should disappear from results. Re-allow it when done:
```bash
sudo ufw allow 8080
```

---

## Phase 3 — Flask Dashboard (Development Skills)

**Goal:** Build a web app that displays scan results, stores history, and alerts on new ports.

---

### Task 7: Write the Database Layer

**What you're learning:** SQLite is a simple file-based database. Every app needs to store data somewhere — this is your first real data persistence layer.

- [ ] Create `F:\IT_Proj\homewatch\db.py`:

```python
import sqlite3
from datetime import datetime

DB_PATH = 'homewatch.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            status TEXT NOT NULL,
            ports_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_scan(target, status, ports):
    """Save a scan result to the database."""
    import json
    conn = get_connection()
    conn.execute(
        'INSERT INTO scans (target, scanned_at, status, ports_json) VALUES (?, ?, ?, ?)',
        (target, datetime.now().isoformat(), status, json.dumps(ports))
    )
    conn.commit()
    conn.close()


def get_recent_scans(target, limit=10):
    """Get the N most recent scans for a target."""
    import json
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM scans WHERE target = ? ORDER BY scanned_at DESC LIMIT ?',
        (target, limit)
    ).fetchall()
    conn.close()

    scans = []
    for row in rows:
        scans.append({
            'id': row['id'],
            'target': row['target'],
            'scanned_at': row['scanned_at'],
            'status': row['status'],
            'ports': json.loads(row['ports_json'])
        })
    return scans


def get_previous_ports(target):
    """Get the port list from the scan before the most recent one."""
    import json
    conn = get_connection()
    rows = conn.execute(
        'SELECT ports_json FROM scans WHERE target = ? ORDER BY scanned_at DESC LIMIT 2',
        (target,)
    ).fetchall()
    conn.close()

    if len(rows) < 2:
        return []
    return json.loads(rows[1]['ports_json'])
```

- [x] Test the database layer by running Python interactively:
```
python
```
Then type:
```python
import db
db.init_db()
db.save_scan('192.168.1.42', 'up', [{'port': 22, 'service': 'ssh'}])
print(db.get_recent_scans('192.168.1.42'))
exit()
```
Expected: prints a list with your test scan. A file `homewatch.db` appears in the folder.

---

### Task 8: Write the Flask App

**What you're learning:** Flask is a web framework — it handles HTTP requests and serves pages. This is the core of web development.

- [x] Create `F:\IT_Proj\homewatch\app.py`:

```python
from flask import Flask, render_template, request, redirect, url_for
import scanner
import db

app = Flask(__name__)

# Initialize the database when the app starts
db.init_db()


@app.route('/')
def index():
    """Main dashboard page."""
    target = request.args.get('target', '')
    scans = []
    current_scan = None
    new_ports = []

    if target:
        scans = db.get_recent_scans(target, limit=10)
        if scans:
            current_scan = scans[0]

    return render_template(
        'index.html',
        target=target,
        current_scan=current_scan,
        scans=scans,
        new_ports=new_ports
    )


@app.route('/scan', methods=['POST'])
def run_scan():
    """Trigger a new scan and save the result."""
    target = request.form.get('target', '').strip()

    if not target:
        return redirect(url_for('index'))

    # Get previous ports before scanning (for comparison)
    previous_ports = db.get_previous_ports(target)
    previous_port_numbers = {p['port'] for p in previous_ports}

    # Run the scan
    result = scanner.scan_host(target)

    # Save to database
    db.save_scan(target, result['status'], result['ports'])

    # Find new ports (ports in this scan not in previous scan)
    current_port_numbers = {p['port'] for p in result['ports']}
    new_port_numbers = current_port_numbers - previous_port_numbers

    # Load full scan history
    scans = db.get_recent_scans(target, limit=10)
    current_scan = scans[0] if scans else None

    # Build list of new port details for alerting
    new_ports = [p for p in result['ports'] if p['port'] in new_port_numbers]

    return render_template(
        'index.html',
        target=target,
        current_scan=current_scan,
        scans=scans,
        new_ports=new_ports
    )


if __name__ == '__main__':
    app.run(debug=True)
```

---

### Task 9: Write the Dashboard Template

- [x] Create the folder `F:\IT_Proj\homewatch\templates\`

- [x] Create `F:\IT_Proj\homewatch\templates\index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HomeWatch</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>

  <div class="container">
    <h1>HomeWatch</h1>
    <p class="subtitle">Network Security Monitor</p>

    <!-- Scan form -->
    <form action="/scan" method="POST" class="scan-form">
      <input
        type="text"
        name="target"
        placeholder="Target IP (e.g. 192.168.1.42)"
        value="{{ target }}"
        required
      >
      <button type="submit">Scan Now</button>
    </form>

    <!-- New port alerts -->
    {% if new_ports %}
    <div class="alert">
      <strong>Alert:</strong> {{ new_ports | length }} new port(s) detected since last scan:
      {% for p in new_ports %}
        <span class="badge new">{{ p.port }}/{{ p.protocol }} ({{ p.service }})</span>
      {% endfor %}
    </div>
    {% endif %}

    <!-- Current scan results -->
    {% if current_scan %}
    <div class="card">
      <h2>Latest Scan — {{ target }}</h2>
      <p>Status: <strong>{{ current_scan.status }}</strong> &nbsp;|&nbsp; Scanned: {{ current_scan.scanned_at }}</p>

      {% if current_scan.ports %}
      <table>
        <thead>
          <tr>
            <th>Port</th>
            <th>Protocol</th>
            <th>Service</th>
            <th>Version</th>
            <th>State</th>
          </tr>
        </thead>
        <tbody>
          {% for port in current_scan.ports %}
          <tr {% if port in new_ports %}class="new-row"{% endif %}>
            <td>{{ port.port }}</td>
            <td>{{ port.protocol }}</td>
            <td>{{ port.service }}</td>
            <td>{{ port.version }}</td>
            <td><span class="badge open">{{ port.state }}</span></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <p>No open ports detected.</p>
      {% endif %}
    </div>

    <!-- Scan history -->
    {% if scans | length > 1 %}
    <div class="card">
      <h2>Scan History</h2>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Status</th>
            <th>Open Ports</th>
          </tr>
        </thead>
        <tbody>
          {% for scan in scans %}
          <tr>
            <td>{{ scan.scanned_at }}</td>
            <td>{{ scan.status }}</td>
            <td>
              {% for p in scan.ports %}
                <span class="badge">{{ p.port }}/{{ p.protocol }}</span>
              {% endfor %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% endif %}

    {% elif target %}
    <div class="card">
      <p>No scans yet for {{ target }}. Click "Scan Now" to start.</p>
    </div>
    {% endif %}

  </div>

</body>
</html>
```

---

### Task 10: Write the Stylesheet

- [x] Create the folder `F:\IT_Proj\homewatch\static\`

- [x] Create `F:\IT_Proj\homewatch\static\style.css`:

```css
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f0f2f5;
  color: #1a1a1a;
  padding: 2rem;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.subtitle {
  color: #64748b;
  margin-bottom: 2rem;
}

.scan-form {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.scan-form input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
}

.scan-form button {
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}

.scan-form button:hover { background: #1d4ed8; }

.alert {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.card h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: #0f172a;
}

.card p {
  color: #475569;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

tr:last-child td { border-bottom: none; }
tr.new-row { background: #fefce8; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  background: #e2e8f0;
  color: #475569;
  margin: 2px;
}

.badge.open { background: #dcfce7; color: #166534; }
.badge.new  { background: #fef3c7; color: #92400e; }
```

---

### Task 11: Run the Full App

- [x] In PowerShell, navigate to your project:
```
cd F:\IT_Proj\homewatch
```

- [x] Start the Flask app:
```
python app.py
```
Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

- [x] Open a browser and go to: `http://localhost:5000`

Expected: You see the HomeWatch dashboard with a text field and "Scan Now" button.

- [x] Enter your Linux laptop's IP and click Scan Now.

Expected:
- Table appears with port 22 (ssh) and port 8080 (http) listed
- Scan history section appears after second scan
- If you open a new port on the Linux machine and scan again, it appears highlighted in yellow with an alert banner

- [x] Run a second scan. Then on the Linux laptop open a new port:
```bash
sudo ufw allow 3000
python3 -m http.server 3000 &
```
Then scan again from the dashboard. Expected: port 3000 appears in the alert banner as a new port.

**Phase 3 complete.** You now have a working web application.

---

## Phase 4 — Portfolio (Git + Documentation)

**Goal:** Publish your project to GitHub so anyone can see what you built.

---

### Task 12: Initialize Git and Create .gitignore

- [x] In PowerShell, in your project folder:
```
cd F:\IT_Proj\homewatch
git init
```

- [x] Create `.gitignore` to exclude the database and Python cache:
```
homewatch.db
__pycache__/
*.pyc
*.pyo
.env
```
Save this as `F:\IT_Proj\homewatch\.gitignore`

- [x] Stage and make your first commit:
```
git add .
git commit -m "feat: initial HomeWatch implementation"
```

---

### Task 13: Create GitHub Repo and Push

- [x] Go to github.com and sign in (create account if needed)

- [x] Click the `+` button → "New repository"
  - Name: `homewatch`
  - Description: `Home network security monitor — Python, Flask, nmap`
  - Set to Public
  - Do NOT initialize with README (you'll add your own)
  - Click "Create repository"

- [x] GitHub will show you commands. Run these in PowerShell:
```
git remote add origin https://github.com/YOURUSERNAME/homewatch.git
git branch -M main
git push -u origin main
```

Expected: your code is now live at `github.com/YOURUSERNAME/homewatch`

---

### Task 14: Write the README

- [ ] Create `F:\IT_Proj\homewatch\README.md`:

```markdown
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

## Screenshots

[Add screenshots of your running dashboard here]
```

- [x] Commit and push the README:
```
git add README.md
git commit -m "docs: add README with setup and architecture"
git push
```

- [x] Take a screenshot of your running dashboard and add it to the GitHub repo (drag and drop into the README editor on github.com).

---

## Success Checklist

- [x] Can SSH from Windows PC into Linux laptop
- [x] `scanner.py` returns accurate open port data as JSON
- [x] Flask dashboard runs at `http://localhost:5000`
- [x] Scan results display in browser with port table
- [x] New ports trigger alert banner
- [x] Scan history shows past 10 runs
- [x] Public GitHub repo live with README and screenshots

---

## What Comes Next (after this project)

Once HomeWatch is complete, natural next steps by area:

**IT:** Set up a full home server (Raspberry Pi or repurposed machine), run services (Nextcloud, Plex, Pi-hole)

**Cybersecurity:** Try TryHackMe beginner rooms, attempt CTF challenges, add vulnerability scanning to HomeWatch

**Development:** Add user authentication to HomeWatch, deploy Flask app to a VPS (DigitalOcean/Linode), learn a frontend framework (React)
