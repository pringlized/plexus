-- Plexus tables — raw SQL.
-- Targets PostgreSQL. For SQLite, swap TIMESTAMPTZ → DATETIME,
-- UUID → TEXT, JSONB → TEXT, and replace gen_random_uuid() with an
-- application-supplied UUID at insert time.

CREATE TABLE IF NOT EXISTS plexus_nodes (
    pinch_id        VARCHAR(12)  PRIMARY KEY,
    name            TEXT,
    layer           TEXT,
    source_file     TEXT         NOT NULL,
    source_function TEXT         NOT NULL,
    source_line     INTEGER      NOT NULL,
    first_seen      TIMESTAMPTZ  DEFAULT now(),
    last_seen       TIMESTAMPTZ  DEFAULT now(),
    ttl_days        INTEGER      DEFAULT 90
);

CREATE TABLE IF NOT EXISTS plexus_action_log (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    pinch_id        VARCHAR(12)  NOT NULL,
    signal_id       UUID         NOT NULL,
    action_name     TEXT         NOT NULL,
    batch_name      TEXT,
    payload         JSONB        NOT NULL,
    severity        TEXT         NOT NULL,
    layer           TEXT,
    node_name       TEXT,
    source_file     TEXT         NOT NULL,
    source_function TEXT         NOT NULL,
    source_line     INTEGER      NOT NULL,
    ok              BOOLEAN      NOT NULL,
    detail          TEXT,
    executed_at     TIMESTAMPTZ  DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_action_log_pinch_id
    ON plexus_action_log (pinch_id);

CREATE INDEX IF NOT EXISTS idx_action_log_action_name
    ON plexus_action_log (action_name);

CREATE TABLE IF NOT EXISTS plexus_topology_views (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT         NOT NULL,
    description TEXT,
    layout_json JSONB        NOT NULL,
    created_at  TIMESTAMPTZ  DEFAULT now(),
    updated_at  TIMESTAMPTZ  DEFAULT now()
);
