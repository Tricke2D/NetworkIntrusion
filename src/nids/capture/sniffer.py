from typing import Callable
from scapy.all import sniff, Packet
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class PacketSniffer:
    def __init__(self, interface: str, on_packet: Callable[[Packet], None]):
        self.interface = interface
        self.on_packet = on_packet

    def start(self, packet_filter: str = "ip", count: int = 0):
        logger.info(f"Mulai capture di interface '{self.interface}' dengan filter '{packet_filter}'")
        sniff(
            iface=self.interface,
            filter=packet_filter,
            prn=self.on_packet,
            store=False,
            count=count,
        )
