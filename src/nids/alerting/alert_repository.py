from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

INSERT_ALERT_SQL = """
    INSERT INTO alerts (flow_id, alert_type, severity, anomaly_score, src_ip)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
"""

class AlertRepository:
    @staticmethod
    def save(flow_id: int, alert_type: str, severity: str, anomaly_score: float, src_ip: str) -> int:
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_ALERT_SQL, (flow_id, alert_type, severity, anomaly_score, src_ip))
                alert_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"Alert #{alert_id} saved: {alert_type} from {src_ip}")
            return alert_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save alert for flow_id={flow_id}: {e}")
            return 0
        finally:
            DBConnector.release_connection(conn)
