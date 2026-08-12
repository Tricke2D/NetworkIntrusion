from nids.features.flow_feature_extractor import FlowFeatures
from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

INSERT_FEATURE_SQL = """
    INSERT INTO flow_features (flow_id, avg_packet_size, packets_per_second,
                                syn_count, syn_ack_ratio, unique_dst_ports_from_src)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

class FeatureRepository:
    @staticmethod
    def save(features: FlowFeatures):
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_FEATURE_SQL, (
                    features.flow_id,
                    features.avg_packet_size,
                    features.packets_per_second,
                    features.syn_count,
                    features.syn_ack_ratio,
                    features.unique_dst_ports_from_src,
                ))
            conn.commit()
            logger.info(f"Features saved for flow_id={features.flow_id}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save features for flow_id={features.flow_id}: {e}")
        finally:
            DBConnector.release_connection(conn)
