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