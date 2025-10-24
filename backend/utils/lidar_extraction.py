"""
LiDAR Elevation Profile Extraction Module
Extracts elevation profiles from .las/.laz LiDAR point cloud files
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
                    if file.endswith(".las") or file.endswith(".laz"):
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

        # Check for local:// URL (for testing with large files)
        if file_url and file_url.startswith("local://"):
            local_path = file_url.replace("local://", "")
            if os.path.exists(local_path):
                print(f"📂 Using local file: {local_path}")
                return local_path
            else:
                print(f"⚠️  Local file not found: {local_path}")
                return None

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

    def _extract_profile_from_relative_lidar(
        self, las_data, lidar_x, lidar_y, lidar_z, trail_coords, las_file_path
    ) -> Dict[str, Any]:
        """
        Extract elevation profile from LiDAR with relative coordinates.
        Creates a profile by sorting points along a path and sampling elevations.

        Args:
            las_data: Loaded LAS/LAZ file
            lidar_x, lidar_y, lidar_z: LiDAR point arrays
            trail_coords: Trail coordinates (for reference length)
            las_file_path: Path to LAS file

        Returns:
            Dictionary with elevation profile data
        """
        print("🔄 Creating elevation profile from relative-coordinate LiDAR")

        # Filter for ground points if classification is available
        try:
            if hasattr(las_data, "classification"):
                classification = las_data.classification
                ground_mask = classification == 2  # Class 2 = Ground

                if np.any(ground_mask):
                    lidar_x = lidar_x[ground_mask]
                    lidar_y = lidar_y[ground_mask]
                    lidar_z = lidar_z[ground_mask]
                    print(f"✅ Filtered to {len(lidar_x):,} ground points (class 2)")
        except Exception as e:
            print(f"⚠️  Ground filtering failed: {e}, using all points")

        # Create a path through the LiDAR points
        # Strategy: Sort points to create a smooth path
        lidar_points = np.column_stack([lidar_x, lidar_y, lidar_z])

        # Find the point with minimum X (start point)
        start_idx = np.argmin(lidar_x)
        start_point = lidar_points[start_idx]

        # Sample points along the spatial extent
        # Use a grid approach: divide the area into segments
        num_samples = min(
            len(trail_coords), 200
        )  # Match trail length or max 200 points

        # Create a path by sorting points by their primary direction
        # Determine primary direction (X or Y has larger range)
        x_range = np.max(lidar_x) - np.min(lidar_x)
        y_range = np.max(lidar_y) - np.min(lidar_y)

        if x_range > y_range:
            # Sort by X coordinate
            sort_indices = np.argsort(lidar_x)
            print(f"   Sorting by X (range: {x_range:.1f}m)")
        else:
            # Sort by Y coordinate
            sort_indices = np.argsort(lidar_y)
            print(f"   Sorting by Y (range: {y_range:.1f}m)")

        sorted_points = lidar_points[sort_indices]

        # Sample evenly along the sorted points, taking the minimum elevation in each segment
        # This helps filter out trees and obstacles by selecting ground-level points
        segment_size = max(1, len(sorted_points) // num_samples)
        sampled_elevations = []

        for i in range(num_samples):
            start_idx = i * segment_size
            end_idx = min(start_idx + segment_size, len(sorted_points))

            if start_idx < len(sorted_points):
                # Take the minimum elevation in this segment (closest to ground)
                segment_elevations = sorted_points[start_idx:end_idx, 2]
                min_elevation = np.min(segment_elevations)
                sampled_elevations.append(min_elevation)

        sampled_elevations = np.array(sampled_elevations)
        sample_indices = np.linspace(
            0, len(sorted_points) - 1, len(sampled_elevations), dtype=int
        )

        # Calculate distances
        distances = []
        cumulative_dist = 0.0
        for i in range(len(sample_indices)):
            if i == 0:
                distances.append(0.0)
            else:
                prev_point = sorted_points[sample_indices[i - 1]]
                curr_point = sorted_points[sample_indices[i]]
                dx = curr_point[0] - prev_point[0]
                dy = curr_point[1] - prev_point[1]
                dist = np.sqrt(dx**2 + dy**2)
                cumulative_dist += dist
                distances.append(cumulative_dist)

        # Convert distances to km
        distances_km = [d / 1000.0 for d in distances]

        print(f"   Sampled {num_samples} points")
        print(
            f"   Elevation range: {np.min(sampled_elevations):.1f}m to {np.max(sampled_elevations):.1f}m"
        )
        print(f"   Total distance: {distances_km[-1]:.2f} km")

        return {
            "success": True,
            "elevations": sampled_elevations.tolist(),
            "distances": distances_km,
            "coordinates": trail_coords[
                :num_samples
            ],  # Use first N trail coords as placeholders
            "lidar_file": os.path.basename(las_file_path),
            "coverage_percent": 100.0,  # Using all LiDAR data
            "search_radius": 0,  # Not applicable
            "total_lidar_points": len(lidar_x),
            "note": "LiDAR uses relative coordinates - profile generated from LiDAR spatial extent",
        }

    def find_matching_lidar_file(
        self,
        trail_coords: List[List[float]],
        trail_name: str = None,
        trail_id: int = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Find LiDAR file that best matches the trail coordinates
        Prioritizes trail_id associations for manually uploaded files

        Args:
            trail_coords: List of [lat, lon] coordinates from trail
            trail_name: Optional trail name to help with matching
            trail_id: Optional trail ID to match against database associations

        Returns:
            Dictionary with LiDAR file metadata or None
        """
        if not self.lidar_files:
            return None

        # FIRST: Check for direct trail_id association (for manually uploaded files)
        if trail_id is not None:
            for lidar_record in self.lidar_files:
                if lidar_record.get("trail_id") == trail_id:
                    print(
                        f"✅ Found LiDAR file associated with trail_id={trail_id}: {lidar_record.get('filename')}"
                    )
                    return lidar_record

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
        trail_id: int = None,
    ) -> Dict[str, Any]:
        """
        Extract elevation profile from LiDAR data along trail path

        Args:
            trail_coords: List of [lat, lon] coordinates
            lidar_record: Dictionary with LiDAR file metadata (or auto-detect)
            search_radius: Radius in meters to search for LiDAR points near each trail point
            trail_id: Optional trail ID to match against database associations

        Returns:
            Dictionary with elevation profile data
        """
        # Auto-detect LiDAR file if not provided
        if lidar_record is None:
            lidar_record = self.find_matching_lidar_file(
                trail_coords, trail_id=trail_id
            )
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

            # Filter for ground points only (classification = 2) if available
            print(f"Total LiDAR points: {len(las_data.points):,}")

            try:
                # Try to get classification data
                if hasattr(las_data, "classification"):
                    classification = las_data.classification
                    ground_mask = classification == 2  # Class 2 = Ground

                    if np.any(ground_mask):
                        lidar_x = las_data.x[ground_mask]
                        lidar_y = las_data.y[ground_mask]
                        lidar_z = las_data.z[ground_mask]
                        print(
                            f"✅ Filtered to {len(lidar_x):,} ground points (class 2)"
                        )
                    else:
                        # No ground classification, use all points but filter by elevation
                        print(
                            "⚠️  No ground classification found, using elevation filtering"
                        )
                        lidar_x = las_data.x
                        lidar_y = las_data.y
                        lidar_z = las_data.z
                else:
                    # No classification field, use all points
                    print("⚠️  No classification field, using all points")
                    lidar_x = las_data.x
                    lidar_y = las_data.y
                    lidar_z = las_data.z
            except Exception as e:
                print(f"⚠️  Classification filtering failed: {e}, using all points")
                lidar_x = las_data.x
                lidar_y = las_data.y
                lidar_z = las_data.z

            print(f"Using {len(lidar_x):,} LiDAR points for elevation extraction")
            print(f"Trail points: {len(trail_coords)}")

            # Check if LiDAR uses relative coordinates (centered near 0,0)
            x_range = (float(las_data.header.x_min), float(las_data.header.x_max))
            y_range = (float(las_data.header.y_min), float(las_data.header.y_max))
            is_relative_coords = (
                abs(x_range[0]) < 1000
                and abs(x_range[1]) < 1000
                and abs(y_range[0]) < 1000
                and abs(y_range[1]) < 1000
            )

            if is_relative_coords:
                print(
                    f"⚠️  LiDAR uses relative coordinates (X: {x_range[0]:.1f} to {x_range[1]:.1f})"
                )
                print(f"   Using LiDAR data directly without coordinate matching")
                # For relative coordinates, use LiDAR data as-is
                return self._extract_profile_from_relative_lidar(
                    las_data, lidar_x, lidar_y, lidar_z, trail_coords, las_file_path
                )

            # Convert trail coordinates to MGA56 for absolute coordinate matching
            mga_coords = self._coords_to_mga56(trail_coords)
            print(f"Using coordinate-based matching (absolute coordinates)")

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
                    # Use the minimum elevation (closest to ground) to avoid trees/obstacles
                    # This gives us the ground level even if there are overhead obstacles
                    nearby_elevations = lidar_z[indices]
                    elevation = np.min(
                        nearby_elevations
                    )  # Use minimum instead of median
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
    lidar_path = os.path.join(os.path.dirname(__file__), "..", "data", "LiDAR")
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
