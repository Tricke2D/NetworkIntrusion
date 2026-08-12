import threading
from dataclasses import dataclass
from nids.detection.zscore_scorer import ZScoreScorer, ZScoreResult
from nids.detection.mahalanobis_scorer import MahalanobisScorer, MahalanobisResult
from nids.detection.isolation_forest_scorer import IsolationForestScorer
from nids.config.settings import settings
from nids.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CompositeVerdict:
    zscore_result: ZScoreResult
    mahalanobis_result: MahalanobisResult | None
    iforest_score: float | None
    votes: dict
    vote_count: int
    is_anomaly: bool

class DetectionEngine:
    def __init__(self):
        self._mahalanobis_scorer = MahalanobisScorer(window_minutes=15)
        self._iforest_scorer = IsolationForestScorer(window_minutes=15)
        self._models_ready = False
        self._lock = threading.Lock()

    def refresh_models(self):
        new_mahalanobis = MahalanobisScorer(window_minutes=15)
        new_iforest = IsolationForestScorer(window_minutes=15)

        mahalanobis_ok = new_mahalanobis.fit()
        iforest_ok = new_iforest.fit()

        with self._lock:
            if mahalanobis_ok:
                self._mahalanobis_scorer = new_mahalanobis
            if iforest_ok:
                self._iforest_scorer = new_iforest
            self._models_ready = mahalanobis_ok or iforest_ok

    def evaluate(self, feature_values: dict) -> CompositeVerdict:
        zscore_result = ZScoreScorer.score(feature_values)
        zscore_vote = zscore_result.is_anomaly_candidate

        with self._lock:
            mahalanobis_scorer = self._mahalanobis_scorer
            iforest_scorer = self._iforest_scorer
            models_ready = self._models_ready

        mahalanobis_result = None
        mahalanobis_vote = False
        iforest_score = None
        iforest_vote = False

        if models_ready:
            try:
                mahalanobis_result = mahalanobis_scorer.score(feature_values)
                mahalanobis_vote = mahalanobis_result.distance > settings.anomaly_mahalanobis_threshold
            except RuntimeError:
                pass

            try:
                iforest_score = iforest_scorer.score(feature_values)
                iforest_vote = iforest_score < settings.anomaly_iforest_threshold
            except RuntimeError:
                pass

        votes = {"zscore": zscore_vote, "mahalanobis": mahalanobis_vote, "iforest": iforest_vote}
        vote_count = sum(votes.values())

        return CompositeVerdict(
            zscore_result=zscore_result,
            mahalanobis_result=mahalanobis_result,
            iforest_score=iforest_score,
            votes=votes,
            vote_count=vote_count,
            is_anomaly=vote_count >= settings.anomaly_min_votes,
        )
