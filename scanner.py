import nmap
import json
from datetime import datetime


PORT_LIST = '22,80,135,443,445,3000,3389,5000,5001,8080,8443,11434,27036'


def scan_host(target_ip):
    nm = nmap.PortScanner()
    nm.scan(hosts=target_ip, arguments=f'-p {PORT_LIST} -T4')

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
