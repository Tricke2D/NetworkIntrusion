from dataclasses import dataclass
from nids.detection.classification.brute_force_detector import BruteForceDetector
from nids.detection.detection_engine import CompositeVerdict

PORT_SCAN_UNIQUE_PORT_THRESHOLD = 20
SYN_FLOOD_RATIO_THRESHOLD = 5.0
SYN_FLOOD_PPS_THRESHOLD = 50.0

@dataclass
class AlertClassification:
    alert_type: str
    severity: str

def classify_alert(feature_values: dict, verdict: CompositeVerdict, is_brute_force: bool) -> AlertClassification:
    if is_brute_force:
        alert_type = "BRUTE_FORCE"
    elif feature_values["unique_dst_ports_from_src"] > PORT_SCAN_UNIQUE_PORT_THRESHOLD:
        alert_type = "PORT_SCAN"
    elif (feature_values["syn_ack_ratio"] > SYN_FLOOD_RATIO_THRESHOLD
          and feature_values["packets_per_second"] > SYN_FLOOD_PPS_THRESHOLD):
        alert_type = "SYN_FLOOD"
    else:
        alert_type = "GENERIC_ANOMALY"

    if verdict.vote_count == 3:
        severity = "HIGH"
    elif verdict.vote_count == 2:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return AlertClassification(alert_type=alert_type, severity=severity)
