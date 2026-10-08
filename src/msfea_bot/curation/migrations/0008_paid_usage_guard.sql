-- Shared paid-call admission and operator control; contains no prompts or IPs.
CREATE TABLE llm_control (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    circuit_until TIMESTAMPTZ,
    reason TEXT NOT NULL DEFAULT ''
);
INSERT INTO llm_control (id) VALUES (1);

CREATE TABLE llm_attempts (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    day DATE NOT NULL DEFAULT ((now() AT TIME ZONE 'UTC')::date),
    model TEXT NOT NULL,
    purpose TEXT NOT NULL,
    outcome TEXT NOT NULL DEFAULT 'reserved',
    input_tokens INTEGER,
    visible_output_tokens INTEGER,
    reasoning_tokens INTEGER,
    charged_tokens BIGINT NOT NULL,
    charged_nano_usd BIGINT NOT NULL,
    reserved_tokens BIGINT NOT NULL,
    reserved_nano_usd BIGINT NOT NULL,
    input_rate DOUBLE PRECISION NOT NULL,
    output_rate DOUBLE PRECISION NOT NULL,
    finished_at TIMESTAMPTZ,
    error_code TEXT
);
CREATE INDEX llm_attempts_day_idx ON llm_attempts (day);
CREATE INDEX llm_attempts_started_idx ON llm_attempts (started_at);

CREATE TABLE abuse_counts (
    kind TEXT NOT NULL,
    key TEXT NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (kind, key)
);
CREATE INDEX abuse_counts_expiry_idx ON abuse_counts (expires_at);

CREATE TABLE llm_guard_events (
    day DATE NOT NULL DEFAULT ((now() AT TIME ZONE 'UTC')::date),
    reason TEXT NOT NULL,
    count BIGINT NOT NULL DEFAULT 1,
    PRIMARY KEY (day, reason)
);
