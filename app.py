import logging
import ipaddress
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import scanner
import db
import config
import alerts

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
db.init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def scheduled_scan():
    log.info('Scheduled scan starting: %s', config.SUBNET)
    try:
        results = scanner.scan_network(config.SUBNET)
        for result in results:
            previous = db.get_previous_ports(result['target'])
            previous_port_numbers = {p['port'] for p in previous}
            db.save_scan(result['target'], result['status'], result['ports'])
            if previous:
                new_ports = [p for p in result['ports'] if p['port'] not in previous_port_numbers]
                if new_ports:
                    log.info('New ports on %s: %s', result['target'], new_ports)
                    alerts.alert_new_ports(result['target'], new_ports)
        log.info('Scheduled scan complete: %d hosts', len(results))
    except Exception as e:
        log.error('Scheduled scan failed: %s', e)


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scan, 'interval', minutes=config.SCAN_INTERVAL_MINUTES, id='network_scan')
scheduler.start()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == config.AUTH_USERNAME and check_password_hash(config.AUTH_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        error = 'Invalid credentials'
        log.warning('Failed login attempt from %s', request.remote_addr)
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    target = request.args.get('target', '')

    if target:
        scans = db.get_recent_scans(target, limit=10)
        current_scan = scans[0] if scans else None
        return render_template(
            'index.html',
            target=target,
            current_scan=current_scan,
            scans=scans,
            new_ports=[],
            all_hosts=[],
            nicknames=config.NICKNAMES
        )

    all_hosts = db.get_all_latest_scans()
    for host in all_hosts:
        host['hostname'] = scanner.resolve_hostname(host['target'])
    return render_template(
        'index.html',
        target='',
        current_scan=None,
        scans=[],
        new_ports=[],
        all_hosts=all_hosts,
        nicknames=config.NICKNAMES
    )


@app.route('/scan', methods=['POST'])
@login_required
def run_scan():
    target = request.form.get('target', '').strip()

    if not target or not valid_ip(target):
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
        new_ports=new_ports,
        all_hosts=[],
        nicknames=config.NICKNAMES
    )


@app.route('/scan-network', methods=['POST'])
@login_required
def run_network_scan():
    log.info('Manual network scan triggered')
    scheduler.modify_job('network_scan', next_run_time=datetime.now())
    return redirect(url_for('index', scanning=1))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
