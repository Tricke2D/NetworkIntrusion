from scapy.all import IP, TCP, send
from nids.utils.logger import get_logger

logger = get_logger(__name__)

def generate_port_scan(target_ip: str = "127.0.0.1", port_range: tuple = (1, 50)):
    """Kirim SYN packet ke port 1-50 untuk simulasi port scan"""
    logger.info(f"Memulai port scan ke {target_ip}, port {port_range[0]}-{port_range[1]}")
    
    for port in range(port_range[0], port_range[1] + 1):
        packet = IP(dst=target_ip) / TCP(dport=port, flags="S")
        send(packet, verbose=False)
        logger.info(f"SYN sent to port {port}")
    
    logger.info("Port scan selesai!")

if __name__ == "__main__":
    generate_port_scan()
