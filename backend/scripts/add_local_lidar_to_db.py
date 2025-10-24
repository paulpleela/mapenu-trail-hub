"""
Add local LiDAR file to database for testing (without uploading to Supabase Storage)

Usage:
    python3 add_local_lidar_to_db.py <file_path> <trail_id>

Examples:
    python3 add_local_lidar_to_db.py data/LiDAR/Coottha_Mt_1.las 51
    python3 add_local_lidar_to_db.py data/LiDAR/trail_1.las 51
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import laspy

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Parse command line arguments
if len(sys.argv) < 3:
    print("❌ Error: Missing required arguments")
    print("\nUsage:")
    print("  python3 add_local_lidar_to_db.py <file_path> <trail_id>")
    print("\nExamples:")
    print("  python3 add_local_lidar_to_db.py data/LiDAR/Coottha_Mt_1.las 51")
    print("  python3 add_local_lidar_to_db.py data/LiDAR/trail_1.las 51")
    exit(1)

lidar_file_path = sys.argv[1]
try:
    trail_id = int(sys.argv[2])
except ValueError:
    print(f"❌ Error: trail_id must be a number, got: {sys.argv[2]}")
    exit(1)

print("=" * 60)
print("Adding Local LiDAR File to Database")
print("=" * 60)

# Check if file exists
if not os.path.exists(lidar_file_path):
    print(f"❌ File not found: {lidar_file_path}")
    print(f"   Current directory: {os.getcwd()}")
    exit(1)

print(f"\n📂 Reading LiDAR file: {lidar_file_path}")

try:
    # Read LiDAR file metadata
    las = laspy.open(lidar_file_path)
    header = las.header

    file_size_mb = os.path.getsize(lidar_file_path) / (1024 * 1024)

    print(f"\n📊 File Info:")
    print(f"   Size: {file_size_mb:.2f} MB")
    print(f"   Points: {header.point_count:,}")
    print(f"   Bounds: X({header.x_min:.1f} to {header.x_max:.1f})")
    print(f"           Y({header.y_min:.1f} to {header.y_max:.1f})")
    print(f"           Z({header.z_min:.1f} to {header.z_max:.1f})")

    # Create database record
    filename = os.path.basename(lidar_file_path)
    lidar_record = {
        "trail_id": trail_id,
        "filename": filename,
        "file_url": f"local://{os.path.abspath(lidar_file_path)}",  # Special local:// URL
        "file_size_mb": round(file_size_mb, 2),
        "point_count": int(header.point_count),
        "min_x": float(header.x_min),
        "max_x": float(header.x_max),
        "min_y": float(header.y_min),
        "max_y": float(header.y_max),
        "min_z": float(header.z_min),
        "max_z": float(header.z_max),
        "las_version": f"{header.version.major}.{header.version.minor}",
        "point_format_id": header.point_format.id,
        "crs_epsg": 28356,  # GDA94 MGA Zone 56
    }

    las.close()

    print(f"\n💾 Inserting into database...")
    print(f"   Trail ID: {lidar_record['trail_id']}")
    print(f"   Filename: {lidar_record['filename']}")
    print(f"   File URL: {lidar_record['file_url']}")

    # Insert into database
    response = supabase.table("lidar_files").insert(lidar_record).execute()

    if response.data:
        print(f"\n✅ Success! LiDAR file added to database")
        print(f"   Database ID: {response.data[0]['id']}")
        print(f"\n📍 This file is now associated with Trail ID: {trail_id}")
        print(f"\n⚠️  Note: The file is stored locally, not in Supabase Storage")
        print(f"   The backend will read it directly from: {lidar_file_path}")
        print(f"\n💡 To view this LiDAR data:")
        print(f"   1. Go to the frontend")
        print(f"   2. Select the trail with ID {trail_id}")
        print(f"   3. Choose 'LiDAR' from the elevation source dropdown")
    else:
        print(f"\n❌ Failed to insert into database")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
