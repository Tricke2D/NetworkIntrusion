ALTER TABLE alerts ADD COLUMN IF NOT EXISTS src_ip INET;
CREATE INDEX IF NOT EXISTS idx_alerts_src_ip_type ON alerts (src_ip, alert_type);
