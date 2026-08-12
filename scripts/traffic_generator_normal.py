import time
import random
import subprocess
from nids.utils.logger import get_logger

logger = get_logger(__name__)

def generate_normal_traffic(duration_seconds: int = 30):
    """Generate traffic dengan ping ke localhost"""
    start = time.time()
    count = 0
    
    while time.time() - start < duration_seconds:
        try:
            # Ping localhost
            subprocess.run(["ping", "-n", "1", "127.0.0.1"], 
                         capture_output=True, timeout=2)
            count += 1
            logger.info(f"Ping #{count} terkirim")
        except Exception as e:
            logger.error(f"Error: {e}")
        
        # Interval acak 1-3 detik
        time.sleep(random.uniform(1, 3))
    
    logger.info(f"Selesai: {count} ping terkirim")

if __name__ == "__main__":
    generate_normal_traffic()
