from dataclasses import dataclass, field
from typing import Optional
import time
from scapy.all import Packet, IP, TCP, UDP
from nids.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PacketInfo:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    size_bytes: int
    timestamp: float
    tcp_flags: dict = field(default_factory=dict)

def parse_packet(packet: Packet) -> Optional[PacketInfo]:
    if not packet.haslayer(IP):
        return None

    ip_layer = packet[IP]
    timestamp = time.time()
    size_bytes = len(packet)

    if packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        flags = _extract_tcp_flags(tcp_layer)
        return PacketInfo(
            src_ip=ip_layer.src,
            dst_ip=ip_layer.dst,
            src_port=tcp_layer.sport,
            dst_port=tcp_layer.dport,
            protocol="TCP",
            size_bytes=size_bytes,
            timestamp=timestamp,
            tcp_flags=flags,
        )

    if packet.haslayer(UDP):
        udp_layer = packet[UDP]
        return PacketInfo(
            src_ip=ip_layer.src,
            dst_ip=ip_layer.dst,
            src_port=udp_layer.sport,
            dst_port=udp_layer.dport,
            protocol="UDP",
            size_bytes=size_bytes,
            timestamp=timestamp,
            tcp_flags={},
        )

    return PacketInfo(
        src_ip=ip_layer.src,
        dst_ip=ip_layer.dst,
        src_port=0,
        dst_port=0,
        protocol="OTHER",
        size_bytes=size_bytes,
        timestamp=timestamp,
        tcp_flags={},
    )

def _extract_tcp_flags(tcp_layer) -> dict:
    flag_str = str(tcp_layer.flags)
    return {
        "SYN": "S" in flag_str,
        "ACK": "A" in flag_str,
        "FIN": "F" in flag_str,
        "RST": "R" in flag_str,
        "PSH": "P" in flag_str,
        "URG": "U" in flag_str,
    }
