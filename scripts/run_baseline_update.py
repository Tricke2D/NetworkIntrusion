import time
from nids.baseline.baseline_calculator import BaselineCalculator
from nids.utils.logger import get_logger

logger = get_logger(__name__)
UPDATE_INTERVAL_SECONDS = 300  # 5 menit

def main():
    logger.info("Baseline update job dimulai")
    while True:
        BaselineCalculator.compute_and_store(window_minutes=5)
        time.sleep(UPDATE_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
