from dataclasses import dataclass, field
from typing import NamedTuple

class FlowKey(NamedTuple):
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

@dataclass
class FlowState:
    key: FlowKey
    start_time: float
    last_seen_time: float
    packet_count: int = 0
    byte_count: int = 0
    flags_seen: dict = field(default_factory=dict)
    is_closed: bool = False

    def register_packet(self, size_bytes: int, tcp_flags: dict, timestamp: float):
        self.packet_count += 1
        self.byte_count += size_bytes
        self.last_seen_time = timestamp
        for flag_name, is_set in tcp_flags.items():
            if is_set:
                self.flags_seen[flag_name] = self.flags_seen.get(flag_name, 0) + 1
        if tcp_flags.get("FIN") or tcp_flags.get("RST"):
            self.is_closed = True
