"""
Only responsibility: write last request timestamp to a file
so the VPS cron script can read it and decide when to restart.
"""
import time

TIMESTAMP_FILE = "/tmp/expressrag_last_request"


def record_request() -> None:
    """Called on every /chat request. Updates the timestamp file."""
    try:
        with open(TIMESTAMP_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass  # never let this break a user request