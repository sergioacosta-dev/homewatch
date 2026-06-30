import smtplib
import ssl
import urllib.request
import logging
import config

log = logging.getLogger(__name__)


def send_email(subject, body):
    if not all([config.SMTP_FROM, config.SMTP_PASSWORD, config.ALERT_EMAIL_TO]):
        log.warning('Email alert skipped: missing config')
        return
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(config.SMTP_FROM, config.SMTP_PASSWORD)
            msg = f'Subject: {subject}\nFrom: {config.SMTP_FROM}\nTo: {config.ALERT_EMAIL_TO}\n\n{body}'
            smtp.sendmail(config.SMTP_FROM, config.ALERT_EMAIL_TO, msg)
        log.info('Alert email sent: %s', subject)
    except Exception as e:
        log.error('Failed to send alert email: %s', e)


def send_push(title, message):
    if not config.NTFY_TOPIC:
        log.warning('Push alert skipped: missing NTFY_TOPIC')
        return
    try:
        req = urllib.request.Request(
            f'https://ntfy.sh/{config.NTFY_TOPIC}',
            data=message.encode(),
            headers={
                'Title': title,
                'Priority': 'high',
                'Tags': 'warning,lock',
            },
            method='POST'
        )
        urllib.request.urlopen(req, timeout=10)
        log.info('Push notification sent: %s', title)
    except Exception as e:
        log.error('Failed to send push notification: %s', e)


def alert_new_ports(host, new_ports):
    parts = [f"{p['port']}/{p['protocol']} ({p['service']})" for p in new_ports]
    port_list = ', '.join(parts)
    title = f'HomeWatch: New port on {host}'
    body = f'New open port(s) detected on {host}:\n{port_list}'
    send_email(title, body)
    send_push(title, body)
