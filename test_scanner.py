"""Minimal self-check for scanner.py's nmap invocation and result parsing.
Run with: python3 test_scanner.py
"""
import unittest
from unittest.mock import patch, MagicMock

import scanner


class ScanHostTests(unittest.TestCase):
    @patch('scanner.nmap.PortScanner')
    def test_uses_top_ports_not_fixed_list(self, mock_scanner_cls):
        mock_nm = MagicMock()
        mock_nm.all_hosts.return_value = []
        mock_scanner_cls.return_value = mock_nm

        scanner.scan_host('192.168.12.50')

        args, kwargs = mock_nm.scan.call_args
        self.assertIn(f'--top-ports {scanner.TOP_PORTS}', kwargs['arguments'])
        self.assertNotIn('-p 22,80,135', kwargs['arguments'])

    @patch('scanner.nmap.PortScanner')
    def test_parses_open_tcp_ports(self, mock_scanner_cls):
        mock_nm = MagicMock()
        mock_nm.all_hosts.return_value = ['192.168.12.50']
        mock_host = MagicMock()
        mock_host.state.return_value = 'up'
        mock_host.__contains__ = lambda self, key: key == 'tcp'
        mock_host.__getitem__ = lambda self, key: {
            22: {'state': 'open', 'name': 'ssh', 'version': ''},
            80: {'state': 'closed', 'name': 'http', 'version': ''},
        }
        mock_nm.__getitem__ = lambda self, key: mock_host
        mock_scanner_cls.return_value = mock_nm

        result = scanner.scan_host('192.168.12.50')

        self.assertEqual(result['status'], 'up')
        self.assertEqual(len(result['ports']), 1)
        self.assertEqual(result['ports'][0]['port'], 22)


if __name__ == '__main__':
    unittest.main()
