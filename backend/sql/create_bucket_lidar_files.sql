-- ===================================================
-- Setup Supabase Storage for LiDAR Files
-- ===================================================
-- Run this in your Supabase SQL Editor

-- 1. Create the storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'lidar-files',
    'lidar-files',
    false,  -- Private bucket (more secure, use signed URLs)
    5368709120,  -- 5GB file size limit
    ARRAY['application/octet-stream']::text[]
)
ON CONFLICT (id) DO NOTHING;

-- 2. Allow authenticated users to upload files
CREATE POLICY "Allow authenticated uploads to lidar-files"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'lidar-files');

-- 3. Allow authenticated users to read their own files
CREATE POLICY "Allow authenticated reads from lidar-files"
ON storage.objects
FOR SELECT
TO authenticated
USING (bucket_id = 'lidar-files');

-- 4. Allow public read access (optional - enable if you want public access)
-- Uncomment the lines below if you want public read access
-- CREATE POLICY "Allow public reads from lidar-files"
-- ON storage.objects
-- FOR SELECT
-- TO public
-- USING (bucket_id = 'lidar-files');

-- 5. Allow authenticated users to delete files (optional)
CREATE POLICY "Allow authenticated deletes from lidar-files"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'lidar-files');

-- 6. Add file_url column to lidar_files table (keep file_path for migration)
ALTER TABLE lidar_files 
ADD COLUMN IF NOT EXISTS file_url TEXT;

-- 7. Create index on file_url for faster queries
CREATE INDEX IF NOT EXISTS idx_lidar_files_url ON lidar_files(file_url);

-- ===================================================
-- Verification Queries
-- ===================================================

-- Check if bucket was created
SELECT * FROM storage.buckets WHERE id = 'lidar-files';

-- Check if policies were created
SELECT * FROM pg_policies WHERE tablename = 'objects' AND policyname LIKE '%lidar-files%';

-- Check if file_url column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'lidar_files' 
AND column_name IN ('file_path', 'file_url');

-- Make bucket public
UPDATE storage.buckets 
SET public = true 
WHERE id = 'lidar-files';

-- Allow public uploads
CREATE POLICY "Allow public uploads to lidar-files"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'lidar-files');

-- Allow public reads
CREATE POLICY "Allow public reads from lidar-files"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'lidar-files');