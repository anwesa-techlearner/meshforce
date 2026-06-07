-- MeshForce Supabase Schema
-- Run this ENTIRE file in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/ioecofskfpchbxbchwdx/editor

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sectors (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  center_lat DOUBLE PRECISION NOT NULL,
  center_lng DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS volunteers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  skills TEXT[] NOT NULL DEFAULT '{}',
  languages TEXT[] NOT NULL DEFAULT '{}',
  sector_id TEXT REFERENCES sectors(id),
  status TEXT NOT NULL DEFAULT 'active_idle'
    CHECK (status IN ('active_idle','on_mission','resting','offline')),
  active_mission_id UUID,
  hours_worked DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  shift_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_mock BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS volunteers_sector_idx ON volunteers(sector_id);
CREATE INDEX IF NOT EXISTS volunteers_status_idx ON volunteers(status);

CREATE TABLE IF NOT EXISTS incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reported_by UUID REFERENCES volunteers(id),
  raw_text TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
  category TEXT NOT NULL CHECK (category IN ('medical','crowd_control','lost_found','infrastructure','general')),
  required_skills TEXT[] NOT NULL DEFAULT '{}',
  summary TEXT NOT NULL,
  sector_id TEXT REFERENCES sectors(id),
  location_lat DOUBLE PRECISION NOT NULL,
  location_lng DOUBLE PRECISION NOT NULL,
  status TEXT NOT NULL DEFAULT 'reported' CHECK (status IN ('reported','dispatched','resolved')),
  assigned_volunteer_ids UUID[] NOT NULL DEFAULT '{}',
  source TEXT NOT NULL DEFAULT 'app' CHECK (source IN ('app','sms')),
  is_mock BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS incidents_status_idx ON incidents(status);

CREATE TABLE IF NOT EXISTS dispatch_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID REFERENCES incidents(id),
  volunteer_id UUID REFERENCES volunteers(id),
  score DOUBLE PRECISION NOT NULL,
  dispatched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO sectors (id, name, center_lat, center_lng) VALUES
  ('SEC-01','Sangam Nose',  25.4244,81.8846),
  ('SEC-02','Triveni Ghat', 25.4358,81.8836),
  ('SEC-03','Parade Ground',25.4484,81.8661),
  ('SEC-04','Jhunsi',       25.4512,81.8340),
  ('SEC-05','Arail',        25.4125,81.9012),
  ('SEC-06','Medical Zone', 25.4390,81.8750)
ON CONFLICT (id) DO NOTHING;

-- Enable Realtime on key tables
ALTER PUBLICATION supabase_realtime ADD TABLE volunteers;
ALTER PUBLICATION supabase_realtime ADD TABLE incidents;
