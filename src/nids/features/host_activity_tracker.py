import threading
from collections import deque, defaultdict

DEFAULT_WINDOW_SECONDS = 60

class HostActivityTracker:
    def __init__(self, window_seconds: int = DEFAULT_WINDOW_SECONDS):
        self._window_seconds = window_seconds
        self._activity: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def register_connection_attempt(self, src_ip: str, dst_port: int, timestamp: float):
        with self._lock:
            self._activity[src_ip].append((timestamp, dst_port))
            self._purge_old_entries(src_ip, timestamp)

    def count_unique_dst_ports(self, src_ip: str, current_time: float) -> int:
        with self._lock:
            self._purge_old_entries(src_ip, current_time)
            entries = self._activity.get(src_ip, deque())
            return len({port for _, port in entries})

    def _purge_old_entries(self, src_ip: str, current_time: float):
        entries = self._activity[src_ip]
        while entries and current_time - entries[0][0] > self._window_seconds:
            entries.popleft()
