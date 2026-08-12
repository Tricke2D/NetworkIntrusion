import time
from scapy.all import Packet
from nids.capture.sniffer import PacketSniffer
from nids.capture.packet_parser import parse_packet
from nids.flow.flow_table import FlowTable
from nids.flow.flow_timeout_manager import FlowTimeoutManager
from nids.flow.flow_state import FlowState
from nids.persistence.flow_repository import FlowRepository
from nids.features.flow_feature_extractor import extract_flow_features
from nids.features.feature_repository import FeatureRepository
from nids.features.host_activity_tracker import HostActivityTracker
from nids.detection.detection_engine import DetectionEngine
from nids.detection.model_refresh_manager import ModelRefreshManager
from nids.detection.classification.brute_force_detector import BruteForceDetector
from nids.detection.classification.alert_classifier import classify_alert
from nids.alerting.alert_cooldown_tracker import AlertCooldownTracker
from nids.alerting.alert_repository import AlertRepository
from nids.alerting.notification_dispatcher import NotificationDispatcher
from nids.config.settings import settings
from nids.utils.logger import get_logger

logger = get_logger(__name__)

def handle_flow_closed(flow: FlowState, host_tracker, detection_engine, brute_force_detector, cooldown_tracker, dispatcher):
    flow_id = FlowRepository.save(flow)
    features = extract_flow_features(flow_id, flow, host_tracker=host_tracker)
    FeatureRepository.save(features)

    duration = flow.last_seen_time - flow.start_time
    brute_force_detector.register_flow_closed(
        flow.key.src_ip, flow.key.dst_ip, flow.key.dst_port, duration, flow.last_seen_time
    )

    feature_values = {
        "avg_packet_size": features.avg_packet_size,
        "packets_per_second": features.packets_per_second,
        "syn_count": features.syn_count,
        "syn_ack_ratio": features.syn_ack_ratio,
        "unique_dst_ports_from_src": features.unique_dst_ports_from_src,
    }
    verdict = detection_engine.evaluate(feature_values)

    if not verdict.is_anomaly:
        return

    is_brute_force = brute_force_detector.is_brute_force_pattern(
        flow.key.src_ip, flow.key.dst_ip, flow.key.dst_port, flow.last_seen_time
    )
    classification = classify_alert(feature_values, verdict, is_brute_force)

    if not cooldown_tracker.should_trigger(flow.key.src_ip, classification.alert_type, time.time()):
        logger.info(f"Alert suppressed by cooldown: {flow.key.src_ip} / {classification.alert_type}")
        return

    anomaly_score = verdict.mahalanobis_result.distance if verdict.mahalanobis_result else verdict.zscore_result.max_zscore
    alert_id = AlertRepository.save(flow_id, classification.alert_type, classification.severity, anomaly_score, flow.key.src_ip)

    detail = f"votes={verdict.vote_count}/3, unique_ports={features.unique_dst_ports_from_src}, zscore_max={verdict.zscore_result.max_zscore}"
    
    dispatcher.dispatch(
        alert_id=alert_id,
        alert_type=classification.alert_type,
        severity=classification.severity,
        src_ip=flow.key.src_ip,
        detail=detail
    )

def main():
    host_tracker = HostActivityTracker(window_seconds=60)
    detection_engine = DetectionEngine()
    detection_engine.refresh_models()
    
    refresh_manager = ModelRefreshManager(detection_engine, refresh_interval_seconds=120)
    refresh_manager.start()

    brute_force_detector = BruteForceDetector(window_seconds=60, min_attempts=10)
    cooldown_tracker = AlertCooldownTracker(cooldown_seconds=settings.alert_cooldown_seconds)
    dispatcher = NotificationDispatcher()

    flow_table = FlowTable(
        on_flow_closed=lambda flow: handle_flow_closed(
            flow, host_tracker, detection_engine, brute_force_detector, cooldown_tracker, dispatcher
        ),
        host_tracker=host_tracker,
    )

    def handle_packet(packet: Packet):
        info = parse_packet(packet)
        if info:
            flow_table.ingest(info)

    timeout_manager = FlowTimeoutManager(flow_table, timeout_seconds=settings.flow_timeout_seconds)
    timeout_manager.start()

    logger.info("NIDS capture pipeline dimulai ? Fase 3 aktif (notification ready)")
    sniffer = PacketSniffer(interface=settings.capture_interface, on_packet=handle_packet)
    sniffer.start(packet_filter="ip")

if __name__ == "__main__":
    main()
