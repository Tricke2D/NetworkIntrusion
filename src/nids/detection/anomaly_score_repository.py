from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

INSERT_SCORE_SQL = """
    INSERT INTO anomaly_scores (flow_id, zscore_composite_count, zscore_max,
                                 mahalanobis_distance, isolation_forest_score)
    VALUES (%s, %s, %s, %s, %s)
"""

class AnomalyScoreRepository:
    @staticmethod
    def save(flow_id: int, zscore_result, mahalanobis_result, iforest_score: float):
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_SCORE_SQL, (
                    flow_id,
                    zscore_result.features_exceeding_threshold,
                    zscore_result.max_zscore,
                    mahalanobis_result.distance if mahalanobis_result else None,
                    iforest_score,
                ))
            conn.commit()
            logger.info(f"Anomaly scores saved for flow_id={flow_id}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save anomaly scores for flow_id={flow_id}: {e}")
        finally:
            DBConnector.release_connection(conn)
