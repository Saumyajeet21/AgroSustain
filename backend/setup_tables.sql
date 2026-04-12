-- ================================================================
-- AgroSustain — Supabase Database Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. Crop Predictions Table
CREATE TABLE IF NOT EXISTS crop_predictions (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lat           FLOAT,
    lon           FLOAT,
    location      TEXT,
    crop          TEXT NOT NULL,
    confidence    FLOAT,
    "N"           FLOAT,  -- Nitrogen
    "P"           FLOAT,  -- Phosphorus
    "K"           FLOAT,  -- Potassium
    temperature   FLOAT,
    humidity      FLOAT,
    ph            FLOAT,
    rainfall      FLOAT,
    top3          JSONB,  -- [{crop, confidence}, ...]
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Disease Diagnoses Table
CREATE TABLE IF NOT EXISTS disease_diagnoses (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plant         TEXT,
    condition     TEXT,
    is_healthy    BOOLEAN,
    confidence    FLOAT,
    gemini_advice TEXT,
    num_leaves    INTEGER,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Chat History Table
CREATE TABLE IF NOT EXISTS chat_history (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id    TEXT NOT NULL,
    role          TEXT NOT NULL,  -- 'user' or 'assistant'
    message       TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_crop_predictions_created ON crop_predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_disease_diagnoses_created ON disease_diagnoses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id, created_at);

-- Enable Row Level Security (allow all for service key)
ALTER TABLE crop_predictions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE disease_diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history      ENABLE ROW LEVEL SECURITY;

-- Service role bypass policies
CREATE POLICY "Service role access crop_predictions"
    ON crop_predictions FOR ALL USING (true);

CREATE POLICY "Service role access disease_diagnoses"
    ON disease_diagnoses FOR ALL USING (true);

CREATE POLICY "Service role access chat_history"
    ON chat_history FOR ALL USING (true);
