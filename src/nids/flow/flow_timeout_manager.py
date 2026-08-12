import threading
import time
from nids.flow.flow_table import FlowTable
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class FlowTimeoutManager:
    def __init__(self, flow_table: FlowTable, timeout_seconds: int, check_interval_seconds: int = 10):
        self._flow_table = flow_table
        self._timeout_seconds = timeout_seconds
        self._check_interval = check_interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        logger.info(f"FlowTimeoutManager mulai, timeout={self._timeout_seconds}s")
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def _run(self):
        while not self._stop_event.is_set():
            self._flow_table.close_idle_flows(self._timeout_seconds, current_time=time.time())
            self._stop_event.wait(self._check_interval)
