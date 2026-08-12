from datetime import datetime
from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

FEATURE_COLUMNS = ["avg_packet_size", "packets_per_second", "syn_count", "syn_ack_ratio", "unique_dst_ports_from_src"]

FETCH_RECENT_FEATURES_SQL = """
    SELECT {columns} FROM flow_features
    WHERE computed_at >= %s
"""

class BaselineRepository:
    @staticmethod
    def fetch_recent_feature_matrix(start: datetime, end: datetime = None) -> list[tuple]:
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                query = FETCH_RECENT_FEATURES_SQL.format(columns=", ".join(FEATURE_COLUMNS))
                cursor.execute(query, (start,))
                rows = cursor.fetchall()
            # Convert Decimal to float for all values
            return [tuple(float(x) if x is not None else 0.0 for x in row) for row in rows]
        finally:
            DBConnector.release_connection(conn)

    @staticmethod
    def save_baseline(feature_name: str, mean: float, std_dev: float, window_start: datetime, window_end: datetime):
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO baseline_stats (feature_name, mean, std_dev, computed_window)
                    VALUES (%s, %s, %s, tstzrange(%s, %s))
                """, (feature_name, mean, std_dev, window_start, window_end))
            conn.commit()
            logger.info(f"Baseline saved for {feature_name}: mean={mean:.4f}, std={std_dev:.4f}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save baseline for {feature_name}: {e}")
        finally:
            DBConnector.release_connection(conn)
