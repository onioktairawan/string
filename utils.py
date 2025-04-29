import time
import psutil
from datetime import datetime, timezone

# Catat waktu mulai bot
BOT_START_TIME = time.time()

def get_uptime() -> str:
    uptime_seconds = time.time() - BOT_START_TIME
    return time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

def get_system_stats() -> dict:
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    }

def get_ping(message_date: datetime) -> float:
    return round((datetime.now(timezone.utc) - message_date).total_seconds() * 1000, 2)
