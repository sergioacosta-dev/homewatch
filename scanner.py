import nmap
import json
import socket
from datetime import datetime


TOP_PORTS = 1000  # nmap's built-in --top-ports N; widened 2026-09-29 from a fixed 13-port allowlist


def scan_host(target_ip):
    nm = nmap.PortScanner()
    nm.scan(hosts=target_ip, arguments=f'--top-ports {TOP_PORTS} -T4')

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


def scan_network(subnet):
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-sn -T4')
    live_hosts = nm.all_hosts()

    results = []
    for host in live_hosts:
        results.append(scan_host(host))
    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python scanner.py <ip_or_subnet>')
        print('       python scanner.py 192.168.12.0/24')
        sys.exit(1)

    target = sys.argv[1]
    print(f'Scanning {target}...')

    if '/' in target:
        results = scan_network(target)
        print(json.dumps(results, indent=2))
    else:
        result = scan_host(target)
        print(json.dumps(result, indent=2))


def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return None
