import threading
from nids.baseline.baseline_calculator import BaselineCalculator
from nids.detection.detection_engine import DetectionEngine
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class ModelRefreshManager:
    def __init__(self, detection_engine: DetectionEngine, refresh_interval_seconds: int = 120):
        self._engine = detection_engine
        self._interval = refresh_interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        logger.info(f"ModelRefreshManager mulai, interval={self._interval}s")
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def _run(self):
        while not self._stop_event.is_set():
            self._refresh_cycle()
            self._stop_event.wait(self._interval)

    def _refresh_cycle(self):
        logger.info("Memulai siklus refresh model...")
        BaselineCalculator.compute_and_store(window_minutes=5)
        self._engine.refresh_models()
        logger.info("Siklus refresh model selesai")
