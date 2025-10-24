CREATE TABLE lidar_files (
    id BIGSERIAL PRIMARY KEY,
    trail_id BIGINT REFERENCES trails(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_url TEXT,  -- Optional: if stored in Supabase Storage or S3
    file_size_mb DECIMAL(10, 2),
    point_count INTEGER,
    
    -- Spatial bounds (in GDA94 MGA Zone 56, EPSG:28356)
    min_x DECIMAL(12, 2),
    max_x DECIMAL(12, 2),
    min_y DECIMAL(12, 2),
    max_y DECIMAL(12, 2),
    min_z DECIMAL(10, 2),  -- Minimum elevation
    max_z DECIMAL(10, 2),  -- Maximum elevation
    
    -- Metadata
    las_version TEXT,
    point_format_id INTEGER,
    crs_epsg INTEGER DEFAULT 28356,  -- Coordinate Reference System
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Quality metrics
    coverage_percent DECIMAL(5, 2),  -- % of trail covered by LiDAR data
    data_quality_score DECIMAL(3, 2),  -- 0-1 quality score
    
    UNIQUE(trail_id, filename)
);

-- Indexes for performance
CREATE INDEX idx_lidar_files_trail_id ON lidar_files(trail_id);
CREATE INDEX idx_lidar_files_bounds ON lidar_files(min_x, max_x, min_y, max_y);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_lidar_files_modtime
    BEFORE UPDATE ON lidar_files
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();