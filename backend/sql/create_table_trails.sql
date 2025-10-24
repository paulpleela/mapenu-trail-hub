-- Supabase table schema for MAPENU trails
-- Run this SQL in your Supabase SQL editor to create the trails table

CREATE TABLE IF NOT EXISTS trails (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    distance DECIMAL(10, 2) NOT NULL DEFAULT 0,
    elevation_gain INTEGER NOT NULL DEFAULT 0,
    elevation_loss INTEGER NOT NULL DEFAULT 0,
    max_elevation INTEGER NOT NULL DEFAULT 0,
    min_elevation INTEGER NOT NULL DEFAULT 0,
    rolling_hills_index DECIMAL(5, 3) NOT NULL DEFAULT 0,
    difficulty_score DECIMAL(4, 1) NOT NULL DEFAULT 0,
    difficulty_level VARCHAR(50) NOT NULL DEFAULT 'Unknown',
    coordinates JSONB NOT NULL DEFAULT '[]'::jsonb,
    elevation_profile JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_trails_difficulty_level ON trails(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_trails_distance ON trails(distance);
CREATE INDEX IF NOT EXISTS idx_trails_created_at ON trails(created_at);
