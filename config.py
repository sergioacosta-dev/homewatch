import os

SUBNET = '192.168.12.0/24'
SCAN_INTERVAL_MINUTES = 15

SECRET_KEY = os.environ.get('SECRET_KEY', '')
AUTH_USERNAME = os.environ.get('AUTH_USERNAME', '')
AUTH_PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', '')
