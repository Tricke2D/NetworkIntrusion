import threading
from typing import Callable, Optional
from nids.capture.packet_parser import PacketInfo
from nids.flow.flow_state import FlowKey, FlowState
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class FlowTable:
    def __init__(self, on_flow_closed: Callable[[FlowState], None], host_tracker=None):
        self._flows: dict[FlowKey, FlowState] = {}
        self._lock = threading.Lock()
        self._on_flow_closed = on_flow_closed
        self._host_tracker = host_tracker

    def _build_key(self, info: PacketInfo) -> FlowKey:
        return FlowKey(
            src_ip=info.src_ip,
            dst_ip=info.dst_ip,
            src_port=info.src_port,
            dst_port=info.dst_port,
            protocol=info.protocol,
        )

    def ingest(self, info: PacketInfo):
        key = self._build_key(info)
        with self._lock:
            flow = self._flows.get(key)
            if flow is None:
                flow = FlowState(key=key, start_time=info.timestamp, last_seen_time=info.timestamp)
                self._flows[key] = flow
                if self._host_tracker:
                    self._host_tracker.register_connection_attempt(
                        info.src_ip, info.dst_port, info.timestamp
                    )
                logger.info(f"Flow baru dibuka: {key}")

            flow.register_packet(info.size_bytes, info.tcp_flags, info.timestamp)

            if flow.is_closed:
                self._close_flow(key)

    def _close_flow(self, key: FlowKey):
        flow = self._flows.pop(key, None)
        if flow:
            logger.info(f"Flow ditutup: {key} | packets={flow.packet_count}")
            self._on_flow_closed(flow)

    def close_idle_flows(self, timeout_seconds: int, current_time: float):
        with self._lock:
            expired_keys = [
                key for key, flow in self._flows.items()
                if current_time - flow.last_seen_time > timeout_seconds
            ]
            for key in expired_keys:
                self._close_flow(key)

    def active_flow_count(self) -> int:
        with self._lock:
            return len(self._flows)
