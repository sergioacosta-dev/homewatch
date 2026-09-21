import sqlite3
import json
from datetime import datetime, timedelta

DB_PATH = 'homewatch.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS login_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            attempted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def record_login_failure(ip):
    conn = get_connection()
    conn.execute(
        'INSERT INTO login_failures (ip, attempted_at) VALUES (?, ?)',
        (ip, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def count_recent_login_failures(ip, window_minutes):
    cutoff = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()
    conn = get_connection()
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM login_failures WHERE ip = ? AND attempted_at > ?',
        (ip, cutoff)
    ).fetchone()
    conn.close()
    return row['n']


def save_scan(target, status, ports):
    conn = get_connection()
    conn.execute(
        'INSERT INTO scans (target, scanned_at, status, ports_json) VALUES (?, ?, ?, ?)',
        (target, datetime.now().isoformat(), status, json.dumps(ports))
    )
    conn.commit()
    conn.close()


def get_recent_scans(target, limit=10):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM scans WHERE target = ? ORDER BY scanned_at DESC LIMIT ?',
        (target, limit)
    ).fetchall()
    conn.close()

    return [
        {
            'id': row['id'],
            'target': row['target'],
            'scanned_at': row['scanned_at'],
            'status': row['status'],
            'ports': json.loads(row['ports_json'])
        }
        for row in rows
    ]


def get_previous_ports(target):
    """Ports from the most recent existing scan, called before the current scan is saved.
    Returns None if no prior scan exists, distinct from [] (a prior scan with no open ports)."""
    conn = get_connection()
    row = conn.execute(
        'SELECT ports_json FROM scans WHERE target = ? ORDER BY scanned_at DESC LIMIT 1',
        (target,)
    ).fetchone()
    conn.close()

    if row is None:
        return None
    return json.loads(row['ports_json'])


def get_all_latest_scans():
    conn = get_connection()
    rows = conn.execute('''
        SELECT s.* FROM scans s
        INNER JOIN (
            SELECT target, MAX(scanned_at) AS latest
            FROM scans
            GROUP BY target
        ) t ON s.target = t.target AND s.scanned_at = t.latest
        ORDER BY s.target
    ''').fetchall()
    conn.close()

    return [
        {
            'id': row['id'],
            'target': row['target'],
            'scanned_at': row['scanned_at'],
            'status': row['status'],
            'ports': json.loads(row['ports_json'])
        }
        for row in rows
    ]
