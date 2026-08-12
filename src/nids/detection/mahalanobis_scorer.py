import numpy as np
from scipy.spatial.distance import mahalanobis
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from nids.baseline.baseline_repository import BaselineRepository, FEATURE_COLUMNS
from nids.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class MahalanobisResult:
    distance: float
    sample_size_used: int

class MahalanobisScorer:
    def __init__(self, window_minutes: int = 15):
        self._window_minutes = window_minutes
        self._mean_vector = None
        self._inv_covariance = None

    def fit(self):
        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(minutes=self._window_minutes)
        rows = BaselineRepository.fetch_recent_feature_matrix(window_start, window_end)

        if len(rows) < len(FEATURE_COLUMNS) + 1:
            logger.warning(f"Sample tidak cukup untuk covariance matrix ({len(rows)} < {len(FEATURE_COLUMNS) + 1})")
            return False

        # Convert all Decimal to float
        matrix = np.array([[float(x) for x in row] for row in rows], dtype=float)
        self._mean_vector = np.mean(matrix, axis=0)

        covariance = np.cov(matrix, rowvar=False)
        covariance += np.eye(covariance.shape[0]) * 1e-6
        self._inv_covariance = np.linalg.inv(covariance)
        logger.info(f"Mahalanobis scorer fitted with {len(rows)} samples")
        return True

    def score(self, feature_values: dict) -> MahalanobisResult:
        if self._mean_vector is None or self._inv_covariance is None:
            raise RuntimeError("Panggil fit() dulu sebelum score()")

        # Convert all values to float
        vector = np.array([float(feature_values.get(name, 0.0)) for name in FEATURE_COLUMNS], dtype=float)
        distance = mahalanobis(vector, self._mean_vector, self._inv_covariance)

        return MahalanobisResult(distance=round(float(distance), 4), sample_size_used=len(self._mean_vector))
