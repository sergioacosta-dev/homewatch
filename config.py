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
