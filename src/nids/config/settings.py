import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "nids_db")
    db_user: str = os.getenv("DB_USER", "nids_user")
    db_password: str = os.getenv("DB_PASSWORD", "nids_pass")
    capture_interface: str = os.getenv("CAPTURE_INTERFACE", "lo")
    flow_timeout_seconds: int = int(os.getenv("FLOW_TIMEOUT_SECONDS", "60"))
    
    # Anomaly detection thresholds
    anomaly_min_votes: int = int(os.getenv("ANOMALY_MIN_VOTES", "2"))
    anomaly_mahalanobis_threshold: float = float(os.getenv("ANOMALY_MAHALANOBIS_THRESHOLD", "3.5"))
    anomaly_iforest_threshold: float = float(os.getenv("ANOMALY_IFOREST_THRESHOLD", "-0.1"))
    alert_cooldown_seconds: int = int(os.getenv("ALERT_COOLDOWN_SECONDS", "300"))
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")

settings = Settings()
