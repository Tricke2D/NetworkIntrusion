ALTER TABLE flow_features
    ADD COLUMN IF NOT EXISTS syn_ack_ratio NUMERIC DEFAULT 0;

CREATE TABLE IF NOT EXISTS anomaly_scores (
    id                      BIGSERIAL PRIMARY KEY,
    flow_id                 BIGINT REFERENCES flows(flow_id) ON DELETE CASCADE,
    zscore_composite_count  INTEGER,
    zscore_max              NUMERIC,
    mahalanobis_distance    NUMERIC,
    isolation_forest_score  NUMERIC,
    computed_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_scores_flow_id ON anomaly_scores (flow_id);
