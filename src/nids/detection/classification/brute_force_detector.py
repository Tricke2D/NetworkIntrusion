import threading
from collections import deque, defaultdict

COMMON_LOGIN_PORTS = {22, 23, 21, 3389, 3306, 5432, 1433, 25}

class BruteForceDetector:
    def __init__(self, window_seconds: int = 60, min_attempts: int = 10, max_flow_duration: float = 2.0):
        self._window_seconds = window_seconds
        self._min_attempts = min_attempts
        self._max_flow_duration = max_flow_duration
        self._attempts: dict[tuple, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def register_flow_closed(self, src_ip: str, dst_ip: str, dst_port: int, duration: float, timestamp: float):
        if dst_port not in COMMON_LOGIN_PORTS or duration > self._max_flow_duration:
            return
        key = (src_ip, dst_ip, dst_port)
        with self._lock:
            self._attempts[key].append(timestamp)
            self._purge_old(key, timestamp)

    def is_brute_force_pattern(self, src_ip: str, dst_ip: str, dst_port: int, current_time: float) -> bool:
        key = (src_ip, dst_ip, dst_port)
        with self._lock:
            self._purge_old(key, current_time)
            return len(self._attempts.get(key, [])) >= self._min_attempts

    def _purge_old(self, key: tuple, current_time: float):
        entries = self._attempts[key]
        while entries and current_time - entries[0] > self._window_seconds:
            entries.popleft()
