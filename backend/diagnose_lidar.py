"""
Diagnostic: Check LiDAR elevation data for trail_1.laz
"""

import laspy
import numpy as np
import os

# Path to the LiDAR file
lidar_file = "data/LiDAR/trail_1.laz"

print("=" * 60)
print("LiDAR File Diagnostics: trail_1.laz")
print("=" * 60)

# Check if file exists
if not os.path.exists(lidar_file):
    print(f"❌ File not found: {lidar_file}")
    print("Looking for files in data/LiDAR/:")
    if os.path.exists("data/LiDAR"):
        for f in os.listdir("data/LiDAR"):
            if f.endswith(".las") or f.endswith(".laz"):
                print(f"  - {f}")
    exit(1)

# Read the LiDAR file
print(f"\n📂 Reading file: {lidar_file}")
las = laspy.read(lidar_file)

print(f"\n📊 BASIC INFO:")
print(f"  Total points: {len(las.points):,}")
print(f"  Point format: {las.point_format}")

print(f"\n🌍 SPATIAL BOUNDS:")
print(f"  X (Easting):  {las.header.x_min:.2f} to {las.header.x_max:.2f} meters")
print(f"  Y (Northing): {las.header.y_min:.2f} to {las.header.y_max:.2f} meters")
print(f"  Z (Elevation): {las.header.z_min:.2f} to {las.header.z_max:.2f} meters")
print(f"  Width:  {las.header.x_max - las.header.x_min:.2f} meters")
print(f"  Height: {las.header.y_max - las.header.y_min:.2f} meters")
print(f"  Elevation range: {las.header.z_max - las.header.z_min:.2f} meters")

print(f"\n📈 ELEVATION STATISTICS:")
z_values = las.z
print(f"  Min elevation: {np.min(z_values):.2f} m")
print(f"  Max elevation: {np.max(z_values):.2f} m")
print(f"  Mean elevation: {np.mean(z_values):.2f} m")
print(f"  Median elevation: {np.median(z_values):.2f} m")
print(f"  Std deviation: {np.std(z_values):.2f} m")
print(f"  Total elevation change: {np.max(z_values) - np.min(z_values):.2f} m")

print(f"\n📍 SAMPLE POINTS (first 10):")
for i in range(min(10, len(las.x))):
    print(f"  Point {i+1}: X={las.x[i]:.2f}, Y={las.y[i]:.2f}, Z={las.z[i]:.2f}")

print(f"\n🎯 ELEVATION DISTRIBUTION:")
# Create bins for elevation histogram
z_min, z_max = np.min(z_values), np.max(z_values)
bins = np.linspace(z_min, z_max, 11)  # 10 bins
hist, bin_edges = np.histogram(z_values, bins=bins)

print(f"  Elevation range    | Point count")
print(f"  {'-'*20}+{'-'*15}")
for i in range(len(hist)):
    bar = "█" * int(hist[i] / max(hist) * 30)
    print(f"  {bin_edges[i]:6.2f} - {bin_edges[i+1]:6.2f} m | {hist[i]:7,} {bar}")

print(f"\n🔍 DIAGNOSIS:")
elevation_range = np.max(z_values) - np.min(z_values)

if elevation_range < 5:
    print(f"  ⚠️  VERY FLAT TERRAIN!")
    print(
        f"     The LiDAR file covers a nearly flat area with only {elevation_range:.2f}m elevation change."
    )
    print(f"     This is normal for small urban areas or flat terrain.")
elif elevation_range < 20:
    print(f"  ℹ️  GENTLY SLOPING TERRAIN")
    print(
        f"     The area has {elevation_range:.2f}m elevation change - moderate slopes."
    )
else:
    print(f"  ✅ SIGNIFICANT ELEVATION CHANGE")
    print(
        f"     The area has {elevation_range:.2f}m elevation change - good for visualization!"
    )

print(f"\n💡 RECOMMENDATION:")
if elevation_range < 5:
    print(f"  - This LiDAR file is for a small, flat area")
    print(f"  - The elevation profile will appear nearly flat (this is correct!)")
    print(
        f"  - Consider using a different LiDAR file if you need more elevation change"
    )
else:
    print(f"  - The elevation data looks good for visualization")
    print(f"  - Make sure the chart Y-axis is properly scaled")

print("\n" + "=" * 60)
