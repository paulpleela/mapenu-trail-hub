-- ===================================================
-- Setup Supabase Storage for XLSX Files
-- ===================================================
-- Run this in your Supabase SQL Editor

-- 1. Create the storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'xlsx-files',
    'xlsx-files',
    false,  -- Private by default (can make public later)
    52428800,  -- 50MB file size limit
    ARRAY['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']::text[]
)
ON CONFLICT (id) DO NOTHING;

-- 2. Allow authenticated users to upload XLSX files
CREATE POLICY "Allow authenticated uploads to xlsx-files"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'xlsx-files');

-- 3. Allow authenticated users to read their own files
CREATE POLICY "Allow authenticated reads from xlsx-files"
ON storage.objects
FOR SELECT
TO authenticated
USING (bucket_id = 'xlsx-files');

-- 4. Allow authenticated users to delete their files (optional)
CREATE POLICY "Allow authenticated deletes from xlsx-files"
ON storage.objects
FOR DELETE
TO authenticated
USING (bucket_id = 'xlsx-files');

-- 5. Add file_url column to xlsx_files table (if it exists)
ALTER TABLE xlsx_files 
ADD COLUMN IF NOT EXISTS file_url TEXT;

-- 6. Create index on file_url for faster lookups
CREATE INDEX IF NOT EXISTS idx_xlsx_files_url ON xlsx_files(file_url);

-- ===================================================
-- Verification Queries
-- ===================================================

-- Check if bucket was created
SELECT * FROM storage.buckets WHERE id = 'xlsx-files';

-- Check if policies were created
SELECT * FROM pg_policies WHERE tablename = 'objects' AND policyname LIKE '%xlsx-files%';

-- Check if file_url column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'xlsx_files' 
AND column_name IN ('file_path', 'file_url');

-- ===================================================
-- Optional: Make Bucket Public
-- ===================================================

-- Make bucket public
UPDATE storage.buckets 
SET public = true 
WHERE id = 'xlsx-files';

-- Allow public uploads
CREATE POLICY "Allow public uploads to xlsx-files"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'xlsx-files');

-- Allow public reads
CREATE POLICY "Allow public reads from xlsx-files"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'xlsx-files');
