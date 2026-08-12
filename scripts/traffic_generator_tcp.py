import socket
import time
import random
from nids.utils.logger import get_logger

logger = get_logger(__name__)

def generate_tcp_traffic(target: str = "127.0.0.1", count: int = 30):
    ports = [80, 443, 8080, 8443, 3306, 5432, 22, 25, 53, 110, 143, 993, 995]
    
    for i in range(count):
        try:
            port = random.choice(ports)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            # Coba koneksi ke port (akan timeout karena tidak ada service, tapi tetap menghasilkan SYN)
            sock.connect((target, port))
            sock.close()
        except Exception:
            pass  # Gagal koneksi, tapi tetap menghasilkan TCP SYN
        
        if (i + 1) % 5 == 0:
            logger.info(f"TCP connection attempt #{i+1} to port {port}")
        
        time.sleep(0.1)  # 100ms interval
    
    logger.info(f"Selesai: {count} TCP connection attempts")

if __name__ == "__main__":
    generate_tcp_traffic(count=50)
