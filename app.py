from flask import Flask, render_template, request, redirect, url_for
import scanner
import db

app = Flask(__name__)

db.init_db()

@app.route('/')
def index():
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
    target = request.form.get('target', '').strip()

    if not target:
        return redirect(url_for('index'))

    previous_ports = db.get_previous_ports(target)
    previous_port_numbers = {p['port'] for p in previous_ports}

    result = scanner.scan_host(target)
    db.save_scan(target, result['status'], result['ports'])

    current_port_numbers = {p['port'] for p in result['ports']}
    new_port_numbers = current_port_numbers - previous_port_numbers

    scans = db.get_recent_scans(target, limit=10)
    current_scan = scans[0] if scans else None
    new_ports = [p for p in result['ports'] if p['port'] in new_port_numbers]

    return render_template(
        'index.html',
        target=target,
        current_scan=current_scan,
        scans=scans,
        new_ports=new_ports
    )

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001, debug=True)