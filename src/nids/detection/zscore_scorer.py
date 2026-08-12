from dataclasses import dataclass
from nids.persistence.db_connector import DBConnector

Z_THRESHOLD = 3.0
MIN_FEATURES_EXCEEDING = 2

FETCH_LATEST_BASELINE_SQL = """
    SELECT DISTINCT ON (feature_name) feature_name, mean, std_dev
    FROM baseline_stats
    ORDER BY feature_name, id DESC
"""

@dataclass
class ZScoreResult:
    per_feature_zscore: dict
    max_zscore: float
    features_exceeding_threshold: int
    is_anomaly_candidate: bool

class ZScoreScorer:
    @staticmethod
    def _get_latest_baseline() -> dict:
        conn = DBConnector.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(FETCH_LATEST_BASELINE_SQL)
                rows = cursor.fetchall()
            # Convert Decimal to float
            return {name: (float(mean), float(std)) for name, mean, std in rows}
        finally:
            DBConnector.release_connection(conn)

    @classmethod
    def score(cls, feature_values: dict) -> ZScoreResult:
        baseline = cls._get_latest_baseline()
        per_feature_zscore = {}

        for name, value in feature_values.items():
            if name not in baseline:
                continue
            mean, std = baseline[name]
            # Convert value to float
            value = float(value)
            z = (value - mean) / std
            per_feature_zscore[name] = round(z, 3)

        exceeding = sum(1 for z in per_feature_zscore.values() if abs(z) > Z_THRESHOLD)
        max_z = max((abs(z) for z in per_feature_zscore.values()), default=0.0)

        return ZScoreResult(
            per_feature_zscore=per_feature_zscore,
            max_zscore=round(max_z, 3),
            features_exceeding_threshold=exceeding,
            is_anomaly_candidate=exceeding >= MIN_FEATURES_EXCEEDING,
        )
