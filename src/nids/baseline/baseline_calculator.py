import numpy as np
from datetime import datetime, timedelta, timezone
from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

TRIM_PERCENTILE = 5
MIN_SAMPLES_REQUIRED = 30

class BaselineCalculator:
    @staticmethod
    def compute_and_store(window_minutes: int = 5):
        # Gunakan UTC time
        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(minutes=window_minutes)
        
        logger.info(f"Fetching data from {window_start} to {window_end} (UTC)")
        
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT avg_packet_size, packets_per_second, syn_count, syn_ack_ratio, unique_dst_ports_from_src
                    FROM flow_features
                    WHERE computed_at >= %s
                """, (window_start,))
                rows = cursor.fetchall()
        finally:
            DBConnector.release_connection(conn)
        
        logger.info(f"Found {len(rows)} rows in window")
        
        if len(rows) < MIN_SAMPLES_REQUIRED:
            logger.warning(
                f"Sample tidak cukup untuk baseline ({len(rows)} < {MIN_SAMPLES_REQUIRED}), skip window ini"
            )
            return

        matrix = np.array(rows, dtype=float)
        feature_names = ["avg_packet_size", "packets_per_second", "syn_count", "syn_ack_ratio", "unique_dst_ports_from_src"]

        for idx, feature_name in enumerate(feature_names):
            column = matrix[:, idx]
            trimmed = _trim_outliers(column, TRIM_PERCENTILE)

            mean = float(np.mean(trimmed))
            std_dev = float(np.std(trimmed)) or 1e-6

            conn = DBConnector.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO baseline_stats (feature_name, mean, std_dev, computed_window)
                        VALUES (%s, %s, %s, tstzrange(%s, %s))
                    """, (feature_name, mean, std_dev, window_start, window_end))
                conn.commit()
                logger.info(f"Baseline updated: {feature_name} mean={mean:.4f} std={std_dev:.4f} (n={len(trimmed)})")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to save baseline for {feature_name}: {e}")
            finally:
                DBConnector.release_connection(conn)

def _trim_outliers(values: np.ndarray, trim_percentile: int) -> np.ndarray:
    lower = np.percentile(values, trim_percentile)
    upper = np.percentile(values, 100 - trim_percentile)
    return values[(values >= lower) & (values <= upper)]
