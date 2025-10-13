"""
LiDAR Elevation Profile Extraction Module
Extracts elevation profiles from .las LiDAR point cloud files
Now supports Supabase Storage with local caching
"""

import laspy
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Transformer
from typing import List, Tuple, Dict, Any, Optional
import os
import requests


class LiDARExtractor:
    def __init__(self, lidar_base_path: str = None, supabase_client=None):
        """
        Initialize LiDAR extractor

        Args:
            lidar_base_path: Path to directory for local cache (default: /tmp/lidar_cache)
            supabase_client: Supabase client instance for database queries
        """
        # Set up cache directory
        self.lidar_base_path = lidar_base_path or "/tmp/lidar_cache"
        os.makedirs(self.lidar_base_path, exist_ok=True)

        # Store supabase client for database queries
        self.supabase = supabase_client

        # Find local files and load from database
        self.lidar_files = self._find_lidar_files()
        print(f"Found {len(self.lidar_files)} LiDAR files")

    def _find_lidar_files(self) -> List[Dict[str, Any]]:
        """
        Find all LiDAR files from database and local cache
        Returns list of dicts with file metadata including URLs
        """
        lidar_records = []

        # Try to get files from Supabase database
        if self.supabase:
            try:
                response = self.supabase.table("lidar_files").select("*").execute()
                if response.data:
                    lidar_records = response.data
                    print(f"📊 Loaded {len(lidar_records)} LiDAR records from database")
            except Exception as e:
                print(f"⚠️  Could not load LiDAR files from database: {e}")

        # Also check for local files (legacy/fallback)
        local_files = []
        if os.path.exists(self.lidar_base_path):
            for root, dirs, files in os.walk(self.lidar_base_path):
                for file in files:
                    if file.endswith(".las"):
                        file_path = os.path.join(root, file)
                        # Add as legacy record if not already in database
                        if not any(r.get("filename") == file for r in lidar_records):
                            local_files.append(
                                {
                                    "filename": file,
                                    "file_path": file_path,
                                    "file_url": None,
                                    "source": "local_cache",
                                }
                            )

        if local_files:
            print(f"📁 Found {len(local_files)} local LiDAR files")
            lidar_records.extend(local_files)

        return lidar_records

    def _download_lidar_file(self, file_url: str, local_cache_path: str) -> str:
        """
        Download LiDAR file from Supabase Storage if not cached locally

        Args:
            file_url: Supabase Storage URL or file path
            local_cache_path: Local path to cache the file

        Returns:
            Path to local cached file
        """
        # If already cached, return immediately
        if os.path.exists(local_cache_path):
            print(f"💾 Using cached LiDAR file: {os.path.basename(local_cache_path)}")
            return local_cache_path

        print(f"☁️  Downloading LiDAR file from Supabase Storage...")

        try:
            # Download from URL
            response = requests.get(file_url, stream=True, timeout=300)
            response.raise_for_status()

            # Save to cache
            os.makedirs(os.path.dirname(local_cache_path), exist_ok=True)
            file_size = 0
            with open(local_cache_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    file_size += len(chunk)

            print(
                f"✅ Cached LiDAR file: {os.path.basename(local_cache_path)} ({file_size/1024/1024:.1f} MB)"
            )
            return local_cache_path

        except Exception as e:
            print(f"❌ Error downloading LiDAR file: {e}")
            raise

    def _get_local_file_path(self, lidar_record: Dict[str, Any]) -> Optional[str]:
        """
        Get local file path for a LiDAR record, downloading from storage if needed

        Args:
            lidar_record: Dictionary with file metadata (file_url, filename, file_path)

        Returns:
            Local file path or None if file not accessible
        """
        filename = lidar_record.get("filename")
        file_url = lidar_record.get("file_url")
        file_path = lidar_record.get("file_path")

        # If we have a local file_path and it exists, use it
        if file_path and os.path.exists(file_path):
            return file_path

        # Otherwise, we need to download from file_url
        if file_url:
            cache_path = os.path.join(self.lidar_base_path, filename)
            try:
                return self._download_lidar_file(file_url, cache_path)
            except Exception as e:
                print(f"⚠️  Could not download {filename}: {e}")
                return None

        return None

    def _coords_to_mga56(self, coords: List[List[float]]) -> List[Tuple[float, float]]:
        """
        Convert WGS84 lat/lon to GDA94 MGA Zone 56 (EPSG:28356)
        Same projection as DEM data

        Args:
            coords: List of [lat, lon] pairs

        Returns:
            List of (easting, northing) tuples
        """
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:28356", always_xy=True)
        converted = []
        for lat, lon in coords:
            x, y = transformer.transform(lon, lat)
            converted.append((x, y))
        return converted

    def find_matching_lidar_file(
        self, trail_coords: List[List[float]], trail_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find LiDAR file that best matches the trail coordinates

        Args:
            trail_coords: List of [lat, lon] coordinates from trail
            trail_name: Optional trail name to help with matching

        Returns:
            Dictionary with LiDAR file metadata or None
        """
        if not self.lidar_files:
            return None

        # Convert trail coords to MGA56
        mga_coords = self._coords_to_mga56(trail_coords)

        # Calculate trail bounding box
        trail_xs = [c[0] for c in mga_coords]
        trail_ys = [c[1] for c in mga_coords]
        trail_bbox = {
            "min_x": min(trail_xs),
            "max_x": max(trail_xs),
            "min_y": min(trail_ys),
            "max_y": max(trail_ys),
        }

        best_match = None
        best_overlap = 0

        # Check each LiDAR file record
        for lidar_record in self.lidar_files:
            try:
                # Get bounds from database record (faster than reading file)
                min_x = lidar_record.get("min_x")
                max_x = lidar_record.get("max_x")
                min_y = lidar_record.get("min_y")
                max_y = lidar_record.get("max_y")

                # Skip if bounds not available in database
                if None in (min_x, max_x, min_y, max_y):
                    print(
                        f"⚠️  No bounds data for {lidar_record.get('filename')}, skipping"
                    )
                    continue

                # Get LiDAR file bounds
                lidar_bbox = {
                    "min_x": float(min_x),
                    "max_x": float(max_x),
                    "min_y": float(min_y),
                    "max_y": float(max_y),
                }

                # Calculate overlap (intersection over trail area)
                overlap_x = max(
                    0,
                    min(trail_bbox["max_x"], lidar_bbox["max_x"])
                    - max(trail_bbox["min_x"], lidar_bbox["min_x"]),
                )
                overlap_y = max(
                    0,
                    min(trail_bbox["max_y"], lidar_bbox["max_y"])
                    - max(trail_bbox["min_y"], lidar_bbox["min_y"]),
                )
                overlap_area = overlap_x * overlap_y

                trail_area = (trail_bbox["max_x"] - trail_bbox["min_x"]) * (
                    trail_bbox["max_y"] - trail_bbox["min_y"]
                )

                if trail_area > 0:
                    overlap_ratio = overlap_area / trail_area

                    # Debug logging
                    print(f"   📊 {lidar_record.get('filename')}:")
                    print(
                        f"      Trail bbox: X({trail_bbox['min_x']:.1f}-{trail_bbox['max_x']:.1f}), Y({trail_bbox['min_y']:.1f}-{trail_bbox['max_y']:.1f})"
                    )
                    print(
                        f"      LiDAR bbox: X({lidar_bbox['min_x']:.1f}-{lidar_bbox['max_x']:.1f}), Y({lidar_bbox['min_y']:.1f}-{lidar_bbox['max_y']:.1f})"
                    )
                    print(
                        f"      Overlap: {overlap_ratio:.1%} ({overlap_x:.1f}m x {overlap_y:.1f}m)"
                    )

                    if overlap_ratio > best_overlap:
                        best_overlap = overlap_ratio
                        best_match = lidar_record

            except Exception as e:
                print(f"❌ Error checking {lidar_record.get('filename')}: {e}")
                continue

        # Lower threshold to 2% for small LiDAR files or long trails
        min_overlap_threshold = 0.02  # 2% minimum overlap

        if best_match and best_overlap > min_overlap_threshold:
            print(
                f"✅ Found matching LiDAR file: {best_match.get('filename')} (overlap: {best_overlap:.1%})"
            )
            return best_match
        else:
            print(
                f"⚠️  No suitable LiDAR file found (best overlap: {best_overlap:.1%}, threshold: {min_overlap_threshold:.1%})"
            )
            return None

    def extract_elevation_profile(
        self,
        trail_coords: List[List[float]],
        lidar_record: Dict[str, Any] = None,
        search_radius: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Extract elevation profile from LiDAR data along trail path

        Args:
            trail_coords: List of [lat, lon] coordinates
            lidar_record: Dictionary with LiDAR file metadata (or auto-detect)
            search_radius: Radius in meters to search for LiDAR points near each trail point

        Returns:
            Dictionary with elevation profile data
        """
        # Auto-detect LiDAR file if not provided
        if lidar_record is None:
            lidar_record = self.find_matching_lidar_file(trail_coords)
            if lidar_record is None:
                return {
                    "success": False,
                    "error": "No matching LiDAR file found",
                    "elevations": [],
                    "coordinates": [],
                }

        # Get local file path (downloads from storage if needed)
        las_file_path = self._get_local_file_path(lidar_record)

        if not las_file_path or not os.path.exists(las_file_path):
            return {
                "success": False,
                "error": f"LiDAR file not accessible: {lidar_record.get('filename')}",
                "elevations": [],
                "coordinates": [],
            }

        try:
            # Read LiDAR data
            print(f"📖 Reading LiDAR file: {os.path.basename(las_file_path)}")
            las_data = laspy.read(las_file_path)

            # Convert trail coordinates to MGA56
            mga_coords = self._coords_to_mga56(trail_coords)

            # Extract LiDAR point cloud coordinates
            lidar_x = las_data.x
            lidar_y = las_data.y
            lidar_z = las_data.z

            print(f"LiDAR points: {len(lidar_x):,}")
            print(f"Trail points: {len(mga_coords)}")

            # Build KD-Tree for efficient nearest neighbor search
            lidar_points = np.column_stack([lidar_x, lidar_y])
            kdtree = cKDTree(lidar_points)

            # Extract elevation for each trail point
            elevations = []
            matched_coords = []

            for i, (x, y) in enumerate(mga_coords):
                # Find all LiDAR points within search radius
                indices = kdtree.query_ball_point([x, y], r=search_radius)

                if indices:
                    # Use median elevation of nearby points (more robust than mean)
                    nearby_elevations = lidar_z[indices]
                    elevation = np.median(nearby_elevations)
                    elevations.append(float(elevation))
                    matched_coords.append(trail_coords[i])
                else:
                    # No nearby points - interpolate or skip
                    if i > 0 and len(elevations) > 0:
                        # Use previous elevation as fallback
                        elevations.append(elevations[-1])
                        matched_coords.append(trail_coords[i])

            coverage = len(elevations) / len(trail_coords) * 100 if trail_coords else 0
            print(
                f"Coverage: {coverage:.1f}% ({len(elevations)}/{len(trail_coords)} points)"
            )

            return {
                "success": True,
                "elevations": elevations,
                "coordinates": matched_coords,
                "lidar_file": os.path.basename(las_file_path),
                "coverage_percent": coverage,
                "search_radius": search_radius,
                "total_lidar_points": len(lidar_x),
            }

        except Exception as e:
            print(f"Error extracting LiDAR elevation: {e}")
            return {
                "success": False,
                "error": str(e),
                "elevations": [],
                "coordinates": [],
            }

    def get_lidar_file_info(self, las_file_path: str) -> Dict[str, Any]:
        """
        Get metadata about a LiDAR file

        Args:
            las_file_path: Path to .las file

        Returns:
            Dictionary with file information
        """
        try:
            las = laspy.open(las_file_path)
            header = las.header

            return {
                "filename": os.path.basename(las_file_path),
                "point_count": header.point_count,
                "bounds": {
                    "min_x": header.x_min,
                    "max_x": header.x_max,
                    "min_y": header.y_min,
                    "max_y": header.y_max,
                    "min_z": header.z_min,
                    "max_z": header.z_max,
                },
                "version": f"{header.version.major}.{header.version.minor}",
                "point_format": header.point_format.id,
            }
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the extractor
    lidar_path = os.path.join(os.path.dirname(__file__), "data", "LiDAR")
    extractor = LiDARExtractor(lidar_path)

    print("\n=== LiDAR Files Found ===")
    for i, file in enumerate(extractor.lidar_files, 1):
        info = extractor.get_lidar_file_info(file)
        print(f"\n{i}. {info.get('filename', 'Unknown')}")
        if "point_count" in info:
            print(f"   Points: {info['point_count']:,}")
            print(
                f"   Z range: {info['bounds']['min_z']:.2f} to {info['bounds']['max_z']:.2f}m"
            )
