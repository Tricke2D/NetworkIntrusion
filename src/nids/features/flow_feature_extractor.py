from dataclasses import dataclass
from nids.flow.flow_state import FlowState

MIN_DURATION_SECONDS = 0.001

@dataclass
class FlowFeatures:
    flow_id: int
    avg_packet_size: float
    packets_per_second: float
    syn_count: int
    syn_ack_ratio: float
    unique_dst_ports_from_src: int = 0

def extract_flow_features(flow_id: int, flow: FlowState, host_tracker=None) -> FlowFeatures:
    duration = max(flow.last_seen_time - flow.start_time, MIN_DURATION_SECONDS)
    
    avg_packet_size = flow.byte_count / flow.packet_count if flow.packet_count else 0.0
    packets_per_second = flow.packet_count / duration
    
    syn_count = flow.flags_seen.get("SYN", 0)
    ack_count = flow.flags_seen.get("ACK", 0)
    syn_ack_ratio = syn_count / max(ack_count, 1)
    
    unique_ports = 0
    if host_tracker:
        unique_ports = host_tracker.count_unique_dst_ports(flow.key.src_ip, flow.last_seen_time)
    
    return FlowFeatures(
        flow_id=flow_id,
        avg_packet_size=round(avg_packet_size, 2),
        packets_per_second=round(packets_per_second, 4),
        syn_count=syn_count,
        syn_ack_ratio=round(syn_ack_ratio, 4),
        unique_dst_ports_from_src=unique_ports,
    )
