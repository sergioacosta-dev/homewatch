import os

SUBNET = '192.168.12.0/24'
SCAN_INTERVAL_MINUTES = 15

SECRET_KEY = os.environ.get('SECRET_KEY', '')
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', '')
AUTH_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', '')

SMTP_FROM = os.environ.get('SMTP_FROM', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
ALERT_EMAIL_TO = os.environ.get('ALERT_EMAIL_TO', '')
NTFY_TOPIC = os.environ.get('NTFY_TOPIC', '')

_REQUIRED = ('SECRET_KEY', 'AUTH_USERNAME', 'AUTH_PASSWORD_HASH')
_missing = [name for name in _REQUIRED if not globals()[name]]
if _missing:
    raise RuntimeError(
        f"Missing required environment variable(s): {', '.join(_missing)}. "
        f"Set them in homewatch.env (see homewatch.env.example)."
    )

NICKNAMES = {
    '192.168.12.1':   'Router',
    '192.168.12.110': 'Kali Desktop',
    '192.168.12.143': 'Windows PC',
    '192.168.12.153': 'Laptop',
}
