import threading

class AlertCooldownTracker:
    def __init__(self, cooldown_seconds: int):
        self._cooldown_seconds = cooldown_seconds
        self._last_alert_time: dict[tuple, float] = {}
        self._lock = threading.Lock()

    def should_trigger(self, src_ip: str, alert_type: str, current_time: float) -> bool:
        key = (src_ip, alert_type)
        with self._lock:
            last = self._last_alert_time.get(key)
            if last is None or current_time - last > self._cooldown_seconds:
                self._last_alert_time[key] = current_time
                return True
            return False
