import logging
from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
import scanner
import db
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)
db.init_db()


def scheduled_scan():
    log.info('Scheduled scan starting: %s', config.SUBNET)
    try:
        results = scanner.scan_network(config.SUBNET)
        for result in results:
            db.save_scan(result['target'], result['status'], result['ports'])
        log.info('Scheduled scan complete: %d hosts', len(results))
    except Exception as e:
        log.error('Scheduled scan failed: %s', e)


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scan, 'interval', minutes=config.SCAN_INTERVAL_MINUTES, id='network_scan')
scheduler.start()


@app.route('/')
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
            all_hosts=[]
        )

    all_hosts = db.get_all_latest_scans()
    return render_template(
        'index.html',
        target='',
        current_scan=None,
        scans=[],
        new_ports=[],
        all_hosts=all_hosts
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
        new_ports=new_ports,
        all_hosts=[]
    )


@app.route('/scan-network', methods=['POST'])
def run_network_scan():
    log.info('Manual network scan triggered')
    scheduled_scan()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
