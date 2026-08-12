import threading
import time
from scapy.all import IP, TCP, send
from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

THREAD_COUNT = 4
PACKETS_PER_THREAD = 2500

def send_burst(thread_id: int, target_ip: str):
    for i in range(PACKETS_PER_THREAD):
        port = 10000 + (thread_id * PACKETS_PER_THREAD) + i
        packet = IP(dst=target_ip) / TCP(dport=port % 65535, flags="S")
        send(packet, verbose=False)

def run_load_test(target_ip: str = "127.0.0.1"):
    logger.info("=" * 60)
    logger.info("LOAD TEST DIMULAI")
    logger.info("=" * 60)
    
    # Hitung flow sebelum
    conn = DBConnector.get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM flows")
        flows_before = cursor.fetchone()[0]
    DBConnector.release_connection(conn)
    logger.info(f"Flow sebelum load test: {flows_before}")

    total_packets = THREAD_COUNT * PACKETS_PER_THREAD
    logger.info(f"Total packet: {total_packets} via {THREAD_COUNT} thread")

    # Kirim packet
    start = time.time()
    threads = [threading.Thread(target=send_burst, args=(i, target_ip)) for i in range(THREAD_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    pps_sent = total_packets / elapsed
    logger.info(f"? Selesai kirim {total_packets} packet dalam {elapsed:.2f}s ({pps_sent:.0f} pps)")

    # Tunggu pipeline selesai proses
    logger.info("Menunggu 10 detik untuk pipeline selesai...")
    time.sleep(10)

    # Hitung flow setelah
    conn = DBConnector.get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM flows")
        flows_after = cursor.fetchone()[0]
    DBConnector.release_connection(conn)

    flows_captured = flows_after - flows_before
    capture_rate = (flows_captured / total_packets) * 100
    
    logger.info("=" * 60)
    logger.info("LOAD TEST SELESAI")
    logger.info(f"Flow setelah: {flows_after}")
    logger.info(f"Flow baru: {flows_captured}")
    logger.info(f"Capture rate: {capture_rate:.1f}%")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_load_test()
