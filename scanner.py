import nmap
import json
from datetime import datetime


def scan_host(target_ip):
    """
    Scan a single host for open ports and running services.
    Returns a dict with host info and list of open ports.
    """
    nm = nmap.PortScanner()
    nm.scan(hosts=target_ip, arguments='-p 22,80,135,443,445,3000,3389,5000,5001,8080,8443,11434,27036 -T4')
    
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


def scan_localhost():
    """
    Scan localhost (127.0.0.1) to capture services only visible locally.
    """
    return scan_host('127.0.0.1')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python scanner.py <ip_address>')
        print('       python scanner.py localhost')
        sys.exit(1)

    target = sys.argv[1]
    if target == 'localhost':
        target = '127.0.0.1'

    print(f'Scanning {target}...')
    result = scan_host(target)
    print(json.dumps(result, indent=2))