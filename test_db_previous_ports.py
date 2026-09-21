"""Self-check for the get_previous_ports off-by-one fix. Run: python3 test_db_previous_ports.py"""
import tempfile
import os
import db

db.DB_PATH = tempfile.mktemp(suffix='.db')
db.init_db()

TARGET = '192.168.12.50'

# No scan yet -> None, not []
assert db.get_previous_ports(TARGET) is None, "expected None before any scan exists"

# First scan saved with no open ports.
db.save_scan(TARGET, 'up', [])

# A prior scan exists (with zero ports) -> must be [], not None.
result = db.get_previous_ports(TARGET)
assert result == [], f"expected [] for a real-but-empty previous scan, got {result!r}"

# Second scan opens port 22 -> "previous" (called before this save) must be the
# first scan's ports ([]), so 22 correctly shows as new.
previous = db.get_previous_ports(TARGET)
db.save_scan(TARGET, 'up', [{'port': 22, 'protocol': 'tcp', 'service': 'ssh'}])
assert previous == [], f"expected previous scan (empty) before saving scan 2, got {previous!r}"

# Third scan (no changes) -> previous must be scan 2's ports ({22}), not scan 1's.
previous = db.get_previous_ports(TARGET)
port_numbers = {p['port'] for p in previous}
assert port_numbers == {22}, f"expected previous={{22}} (the immediately preceding scan), got {port_numbers}"

os.remove(db.DB_PATH)
print("OK")
