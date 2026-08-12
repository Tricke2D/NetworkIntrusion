from nids.persistence.db_connector import DBConnector
from nids.detection.zscore_scorer import ZScoreScorer
from nids.detection.mahalanobis_scorer import MahalanobisScorer
from nids.detection.isolation_forest_scorer import IsolationForestScorer
from nids.detection.anomaly_score_repository import AnomalyScoreRepository
from nids.baseline.baseline_repository import FEATURE_COLUMNS
from nids.utils.logger import get_logger

logger = get_logger(__name__)

FETCH_UNSCORED_SQL = f"""
    SELECT ff.flow_id, {", ".join("ff." + c for c in FEATURE_COLUMNS)}
    FROM flow_features ff
    LEFT JOIN anomaly_scores ans ON ans.flow_id = ff.flow_id
    WHERE ans.id IS NULL
    ORDER BY ff.id DESC
    LIMIT 100
"""

def fetch_unscored_flows():
    conn = DBConnector.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(FETCH_UNSCORED_SQL)
            return cursor.fetchall()
    finally:
        DBConnector.release_connection(conn)

def run_scoring_cycle():
    mahalanobis_scorer = MahalanobisScorer(window_minutes=15)
    iforest_scorer = IsolationForestScorer(window_minutes=15)

    mahalanobis_ready = mahalanobis_scorer.fit()
    iforest_ready = iforest_scorer.fit()

    rows = fetch_unscored_flows()
    logger.info(f"Scoring {len(rows)} flow yang belum di-score")

    anomaly_count = 0
    for row in rows:
        flow_id = row[0]
        feature_values = dict(zip(FEATURE_COLUMNS, row[1:]))

        zscore_result = ZScoreScorer.score(feature_values)
        mahalanobis_result = mahalanobis_scorer.score(feature_values) if mahalanobis_ready else None
        iforest_score = iforest_scorer.score(feature_values) if iforest_ready else None

        AnomalyScoreRepository.save(flow_id, zscore_result, mahalanobis_result, iforest_score)

        if zscore_result.is_anomaly_candidate:
            anomaly_count += 1
            logger.warning(
                f"[ANOMALY CANDIDATE] flow_id={flow_id} | "
                f"zscore_exceeding={zscore_result.features_exceeding_threshold} | "
                f"zscore_max={zscore_result.max_zscore} | "
                f"mahalanobis={mahalanobis_result.distance if mahalanobis_result else 'N/A'} | "
                f"iforest={iforest_score}"
            )

    logger.info(f"Scoring selesai. Found {anomaly_count} anomaly candidates")

def main():
    logger.info("Anomaly scoring job dimulai")
    run_scoring_cycle()

if __name__ == "__main__":
    main()
