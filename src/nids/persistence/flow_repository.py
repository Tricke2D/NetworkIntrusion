import json
from datetime import datetime
from psycopg2.extras import Json
from nids.flow.flow_state import FlowState
from nids.persistence.db_connector import DBConnector
from nids.utils.logger import get_logger

logger = get_logger(__name__)

INSERT_FLOW_RETURNING_SQL = """
    INSERT INTO flows (src_ip, dst_ip, src_port, dst_port, protocol,
                        packet_count, byte_count, start_time, end_time, flags_seen)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING flow_id
"""

class FlowRepository:
    @staticmethod
    def save(flow: FlowState) -> int:
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(INSERT_FLOW_RETURNING_SQL, (
                    flow.key.src_ip,
                    flow.key.dst_ip,
                    flow.key.src_port,
                    flow.key.dst_port,
                    flow.key.protocol,
                    flow.packet_count,
                    flow.byte_count,
                    datetime.fromtimestamp(flow.start_time),
                    datetime.fromtimestamp(flow.last_seen_time),
                    Json(flow.flags_seen),
                ))
                flow_id = cursor.fetchone()[0]
            conn.commit()
            logger.info(f"Flow {flow.key} saved with ID {flow_id}")
            return flow_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save flow {flow.key}: {e}")
            raise
        finally:
            DBConnector.release_connection(conn)
