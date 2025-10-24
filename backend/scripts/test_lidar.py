"""
Test script to inspect LiDAR .las file structure
"""

import laspy
import numpy as np
import os


def inspect_las_file(las_path):
    """Inspect a LiDAR .las file and print its structure"""
    print(f"\n{'='*60}")
    print(f"Inspecting: {os.path.basename(las_path)}")
    print(f"{'='*60}")

    las_data = laspy.read(las_path)

    print(f"\n📊 BASIC INFO:")
    print(f"  Point format: {las_data.point_format}")
    print(f"  Total points: {len(las_data.points):,}")
    print(f"  LAS version: {las_data.header.version}")

    print(f"\n📐 AVAILABLE DIMENSIONS:")
    dims = list(las_data.point_format.dimension_names)
    for dim in dims:
        print(f"  - {dim}")

    print(f"\n🌍 COORDINATE SYSTEM INFO:")
    print(f"  X range: {las_data.header.x_min:.2f} to {las_data.header.x_max:.2f}")
    print(f"  Y range: {las_data.header.y_min:.2f} to {las_data.header.y_max:.2f}")
    print(
        f"  Z range (elevation): {las_data.header.z_min:.2f} to {las_data.header.z_max:.2f}"
    )

    print(f"\n🔢 SCALE & OFFSET:")
    print(f"  X scale: {las_data.header.x_scale}, offset: {las_data.header.x_offset}")
    print(f"  Y scale: {las_data.header.y_scale}, offset: {las_data.header.y_offset}")
    print(f"  Z scale: {las_data.header.z_scale}, offset: {las_data.header.z_offset}")

    print(f"\n📍 FIRST 5 POINTS SAMPLE:")
    print(f"  X: {las_data.x[:5]}")
    print(f"  Y: {las_data.y[:5]}")
    print(f"  Z: {las_data.z[:5]}")

    # Try to get CRS
    try:
        crs = las_data.header.parse_crs()
        print(f"\n🗺️  CRS FOUND: {crs}")
    except Exception as e:
        print(f"\n⚠️  No CRS information found: {e}")

    # Check if coordinates look like lat/lon or projected
    x_sample = las_data.x[0]
    if -180 <= x_sample <= 180:
        print(f"\n💡 Coordinates appear to be in GEOGRAPHIC (lat/lon) format")
    else:
        print(f"\n💡 Coordinates appear to be in PROJECTED (e.g., UTM, MGA) format")

    return las_data


if __name__ == "__main__":
    # Inspect trail_1.las
    las_file = os.path.join(os.path.dirname(__file__), "data", "LiDAR", "trail_1.las")

    if os.path.exists(las_file):
        las_data = inspect_las_file(las_file)

        print(f"\n\n{'='*60}")
        print("SUMMARY: LiDAR Data Contains")
        print(f"{'='*60}")
        print("✅ X, Y coordinates (spatial location)")
        print("✅ Z values (elevation)")
        print("✅ Sufficient for elevation profile extraction")
        print("\nNext steps:")
        print("1. Create extraction function to map GPX coordinates to LiDAR points")
        print("2. Extract elevation along trail path")
        print("3. Compare with GPX and DEM data")
    else:
        print(f"❌ File not found: {las_file}")
