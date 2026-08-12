CREATE TABLE IF NOT EXISTS flows (
    flow_id         BIGSERIAL PRIMARY KEY,
    src_ip          INET NOT NULL,
    dst_ip          INET NOT NULL,
    src_port        INTEGER NOT NULL,
    dst_port        INTEGER NOT NULL,
    protocol        VARCHAR(10) NOT NULL,
    packet_count    INTEGER NOT NULL DEFAULT 0,
    byte_count      BIGINT NOT NULL DEFAULT 0,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    flags_seen      JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_flows_5tuple
    ON flows (src_ip, dst_ip, src_port, dst_port, protocol);
CREATE INDEX IF NOT EXISTS idx_flows_start_time ON flows (start_time);

CREATE TABLE IF NOT EXISTS flow_features (
    id                          BIGSERIAL PRIMARY KEY,
    flow_id                     BIGINT REFERENCES flows(flow_id) ON DELETE CASCADE,
    avg_packet_size             NUMERIC,
    packets_per_second          NUMERIC,
    syn_count                   INTEGER DEFAULT 0,
    unique_dst_ports_from_src   INTEGER DEFAULT 0,
    computed_at                 TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alerts (
    id              BIGSERIAL PRIMARY KEY,
    flow_id         BIGINT REFERENCES flows(flow_id) ON DELETE SET NULL,
    alert_type      VARCHAR(50) NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    anomaly_score   NUMERIC NOT NULL,
    triggered_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS baseline_stats (
    id                BIGSERIAL PRIMARY KEY,
    feature_name      VARCHAR(100) NOT NULL,
    mean              NUMERIC NOT NULL,
    std_dev           NUMERIC NOT NULL,
    computed_window   TSTZRANGE NOT NULL
);
