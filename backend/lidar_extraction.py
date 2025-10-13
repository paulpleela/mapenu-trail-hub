"""
LiDAR Elevation Profile Extraction Module
Extracts elevation profiles from .las LiDAR point cloud files
"""

import laspy
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Transformer
from typing import List, Tuple, Dict, Any
import os


class LiDARExtractor:
    def __init__(self, lidar_base_path: str):
        """
        Initialize LiDAR extractor

        Args:
            lidar_base_path: Path to directory containing .las files
        """
        self.lidar_base_path = lidar_base_path
        self.lidar_files = self._find_lidar_files()
        print(f"Found {len(self.lidar_files)} LiDAR files")

    def _find_lidar_files(self) -> List[str]:
        """Find all .las files in the directory"""
        las_files = []
        for root, dirs, files in os.walk(self.lidar_base_path):
            for file in files:
                if file.endswith(".las"):
                    las_files.append(os.path.join(root, file))
        return las_files

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
    ) -> str:
        """
        Find LiDAR file that best matches the trail coordinates

        Args:
            trail_coords: List of [lat, lon] coordinates from trail
            trail_name: Optional trail name to help with matching

        Returns:
            Path to best matching .las file or None
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

        # Check each LiDAR file
        for las_file in self.lidar_files:
            try:
                # Read header only for efficiency
                las_header = laspy.open(las_file).header

                # Get LiDAR file bounds
                lidar_bbox = {
                    "min_x": las_header.x_min,
                    "max_x": las_header.x_max,
                    "min_y": las_header.y_min,
                    "max_y": las_header.y_max,
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

                    if overlap_ratio > best_overlap:
                        best_overlap = overlap_ratio
                        best_match = las_file

            except Exception as e:
                print(f"Error checking {os.path.basename(las_file)}: {e}")
                continue

        if best_match and best_overlap > 0.5:  # At least 50% overlap
            print(
                f"Found matching LiDAR file: {os.path.basename(best_match)} (overlap: {best_overlap:.1%})"
            )
            return best_match
        else:
            print(f"No suitable LiDAR file found (best overlap: {best_overlap:.1%})")
            return None

    def extract_elevation_profile(
        self,
        trail_coords: List[List[float]],
        las_file_path: str = None,
        search_radius: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Extract elevation profile from LiDAR data along trail path

        Args:
            trail_coords: List of [lat, lon] coordinates
            las_file_path: Path to specific .las file (or auto-detect)
            search_radius: Radius in meters to search for LiDAR points near each trail point

        Returns:
            Dictionary with elevation profile data
        """
        # Auto-detect LiDAR file if not provided
        if las_file_path is None:
            las_file_path = self.find_matching_lidar_file(trail_coords)
            if las_file_path is None:
                return {
                    "success": False,
                    "error": "No matching LiDAR file found",
                    "elevations": [],
                    "coordinates": [],
                }

        # Check if file exists
        if not os.path.exists(las_file_path):
            return {
                "success": False,
                "error": f"LiDAR file not found: {las_file_path}",
                "elevations": [],
                "coordinates": [],
            }

        try:
            # Read LiDAR data
            print(f"Reading LiDAR file: {os.path.basename(las_file_path)}")
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
