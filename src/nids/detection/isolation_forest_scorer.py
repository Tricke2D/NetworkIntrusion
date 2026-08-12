import numpy as np
from datetime import datetime, timedelta, timezone
from sklearn.ensemble import IsolationForest
from nids.baseline.baseline_repository import BaselineRepository, FEATURE_COLUMNS
from nids.utils.logger import get_logger

logger = get_logger(__name__)

class IsolationForestScorer:
    def __init__(self, window_minutes: int = 15, contamination: float = 0.05):
        self._window_minutes = window_minutes
        self._model = IsolationForest(contamination=contamination, random_state=42)
        self._is_fitted = False

    def fit(self):
        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(minutes=self._window_minutes)
        rows = BaselineRepository.fetch_recent_feature_matrix(window_start, window_end)

        if len(rows) < 30:
            logger.warning(f"Sample tidak cukup untuk Isolation Forest ({len(rows)} < 30)")
            return False

        # Convert all Decimal to float
        matrix = np.array([[float(x) for x in row] for row in rows], dtype=float)
        self._model.fit(matrix)
        self._is_fitted = True
        logger.info(f"Isolation Forest fitted with {len(rows)} samples")
        return True

    def score(self, feature_values: dict) -> float:
        if not self._is_fitted:
            raise RuntimeError("Panggil fit() dulu sebelum score()")

        # Convert all values to float
        vector = np.array([[float(feature_values.get(name, 0.0)) for name in FEATURE_COLUMNS]], dtype=float)
        score = self._model.decision_function(vector)[0]
        return round(float(score), 4)
