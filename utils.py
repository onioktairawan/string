from datetime import datetime, timezone
import psutil, platform

start_time = datetime.now()

def get_uptime():
    delta = datetime.now() - start_time
    return str(delta).split('.')[0]

def get_latency(message_date):
    message_date = message_date.astimezone(timezone.utc)
    now = datetime.now(timezone.utc)
    return round((now - message_date).total_seconds() * 1000, 2)

def get_cpu_info():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    return f"{cpu_percent}% (Platform: {platform.system()})"
