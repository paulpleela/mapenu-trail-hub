import laspy
import numpy as np
import matplotlib.pyplot as plt
import gpxpy
from pathlib import Path
import zipfile
import tempfile
import os
import shutil
from math import radians, sin, cos, sqrt, atan2

class TrailLiDARAnalyzer:
    def __init__(self, lidar_folder_path, gpx_file_path):
        self.lidar_folder = Path(lidar_folder_path)
        self.gpx_file = Path(gpx_file_path)
        self.trail_coords = []
        self.point_clouds = []
        
    def load_gpx_trail(self):
        """Load GPX trail coordinates"""
        with open(self.gpx_file, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.trail_coords.append([point.longitude, point.latitude])
        
        print(f"Loaded {len(self.trail_coords)} trail points")
        return self.trail_coords
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two lat/lon points in meters"""
        R = 6371000  # Earth radius in meters
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def find_relevant_lidar_files(self, buffer_distance=500):
        """Find LiDAR files that contain points near the trail"""
        if not self.trail_coords:
            self.load_gpx_trail()
        
        # Get trail bounds with buffer
        lons = [coord[0] for coord in self.trail_coords]
        lats = [coord[1] for coord in self.trail_coords]
        
        # Convert buffer distance to approximate degrees
        buffer_deg = buffer_distance / 111000  # Rough conversion
        
        min_lon, max_lon = min(lons) - buffer_deg, max(lons) + buffer_deg
        min_lat, max_lat = min(lats) - buffer_deg, max(lats) + buffer_deg
        
        print(f"Searching for LiDAR files in bounds: {min_lon:.6f}, {min_lat:.6f} to {max_lon:.6f}, {max_lat:.6f}")
        
        # Find LiDAR zip files
        lidar_files = list(self.lidar_folder.glob("**/*.zip"))
        relevant_files = []
        
        for zip_file in lidar_files:
            # Parse coordinates from filename
            # Format: Brisbane_YYYY_LGA_SW_XXXXXX_YYYYYYY_1K_Las.zip
            try:
                parts = zip_file.stem.split('_')
                if len(parts) >= 7:
                    easting = int(parts[-4])  # X coordinate (UTM)
                    northing = int(parts[-3])  # Y coordinate (UTM)
                    
                    # Convert UTM to lat/lon (approximate for zone 56)
                    # This is a rough conversion - for production use proper UTM conversion
                    lon = (easting - 500000) / 111000 + 153.0  # Rough UTM Zone 56 conversion
                    lat = northing / 111000 - 27.0  # Rough conversion for Brisbane area
                    
                    # Check if this tile might contain trail points
                    if (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                        relevant_files.append(zip_file)
                        print(f"Found relevant LiDAR file: {zip_file.name}")
                        
            except (ValueError, IndexError) as e:
                print(f"Could not parse coordinates from {zip_file.name}: {e}")
                continue
        
        return relevant_files
    
    def extract_and_load_las_files(self, zip_files, temp_dir=None):
        """Extract LAS files from zip archives and load point cloud data"""
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        point_clouds = []
        
        for zip_file in zip_files[:3]:  # Limit to first 3 files for memory reasons
            try:
                print(f"Processing {zip_file.name}...")
                
                # Extract zip file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find LAS files in extracted content
                las_files = list(Path(temp_dir).glob("**/*.las")) + list(Path(temp_dir).glob("**/*.laz"))
                
                for las_file in las_files:
                    try:
                        # Load LAS file
                        las = laspy.read(str(las_file))
                        
                        # Extract coordinates and classification
                        x = las.x
                        y = las.y
                        z = las.z
                        
                        # Get point classifications if available
                        if hasattr(las, 'classification'):
                            classification = las.classification
                        else:
                            classification = np.zeros(len(x))
                        
                        # Get intensity if available
                        if hasattr(las, 'intensity'):
                            intensity = las.intensity
                        else:
                            intensity = np.zeros(len(x))
                        
                        point_cloud = {
                            'filename': las_file.name,
                            'x': x,
                            'y': y,
                            'z': z,
                            'classification': classification,
                            'intensity': intensity,
                            'point_count': len(x)
                        }
                        
                        point_clouds.append(point_cloud)
                        print(f"Loaded {len(x):,} points from {las_file.name}")
                        
                    except Exception as e:
                        print(f"Error loading {las_file}: {e}")
                        continue
                
                # Clean up extracted files for this zip
                for las_file in las_files:
                    try:
                        las_file.unlink()
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error processing {zip_file}: {e}")
                continue
        
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        self.point_clouds = point_clouds
        return point_clouds
    
    def analyze_trail_corridor(self, corridor_width=50):
        """Analyze point cloud data within a corridor around the trail"""
        if not self.trail_coords or not self.point_clouds:
            print("Trail coordinates and point clouds must be loaded first")
            return None
        
        corridor_points = []
        
        for pc in self.point_clouds:
            print(f"Analyzing {pc['filename']} with {pc['point_count']:,} points...")
            
            # Convert UTM coordinates to lat/lon (approximate)
            pc_lons = (pc['x'] - 500000) / 111000 + 153.0
            pc_lats = pc['y'] / 111000 - 27.0
            
            # Find points within corridor
            for i, trail_coord in enumerate(self.trail_coords):
                trail_lon, trail_lat = trail_coord
                
                # Find nearby points
                distances = []
                for j in range(len(pc_lons)):
                    dist = self.haversine_distance(trail_lat, trail_lon, pc_lats[j], pc_lons[j])
                    if dist <= corridor_width:
                        distances.append(dist)
                        
                        corridor_points.append({
                            'trail_point_index': i,
                            'trail_lon': trail_lon,
                            'trail_lat': trail_lat,
                            'pc_x': pc['x'][j],
                            'pc_y': pc['y'][j],
                            'pc_z': pc['z'][j],
                            'pc_lon': pc_lons[j],
                            'pc_lat': pc_lats[j],
                            'distance_to_trail': dist,
                            'classification': pc['classification'][j],
                            'intensity': pc['intensity'][j],
                            'source_file': pc['filename']
                        })
                
                if i % 100 == 0:
                    print(f"Processed {i}/{len(self.trail_coords)} trail points")
        
        print(f"Found {len(corridor_points)} LiDAR points within {corridor_width}m of trail")
        return corridor_points
    
    def create_lidar_visualization(self, corridor_points, output_path="trail_lidar_analysis.png"):
        """Create comprehensive LiDAR visualizations"""
        if not corridor_points:
            print("No corridor points available for visualization")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Extract data for plotting
        trail_indices = [p['trail_point_index'] for p in corridor_points]
        elevations = [p['pc_z'] for p in corridor_points]
        distances_to_trail = [p['distance_to_trail'] for p in corridor_points]
        classifications = [p['classification'] for p in corridor_points]
        intensities = [p['intensity'] for p in corridor_points]
        
        # 1. Elevation vs Trail Position
        ax1.scatter(trail_indices, elevations, c=distances_to_trail, cmap='viridis', s=1, alpha=0.6)
        ax1.set_xlabel('Trail Point Index')
        ax1.set_ylabel('Elevation (m)')
        ax1.set_title('LiDAR Elevations Along Trail')
        cbar1 = plt.colorbar(ax1.collections[0], ax=ax1)
        cbar1.set_label('Distance to Trail (m)')
        
        # 2. Point Classification Distribution
        unique_classes, class_counts = np.unique(classifications, return_counts=True)
        class_labels = {
            0: 'Never Classified',
            1: 'Unclassified',
            2: 'Ground',
            3: 'Low Vegetation',
            4: 'Medium Vegetation',
            5: 'High Vegetation',
            6: 'Building',
            9: 'Water',
            17: 'Bridge'
        }
        
        labels = [class_labels.get(cls, f'Class {cls}') for cls in unique_classes]
        ax2.pie(class_counts, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('LiDAR Point Classification Distribution')
        
        # 3. Cross-sectional View (elevation vs distance from trail centerline)
        ax3.scatter(distances_to_trail, elevations, c=classifications, cmap='tab10', s=1, alpha=0.6)
        ax3.set_xlabel('Distance from Trail Centerline (m)')
        ax3.set_ylabel('Elevation (m)')
        ax3.set_title('Trail Cross-Section Profile')
        
        # 4. Intensity Analysis
        if any(i > 0 for i in intensities):
            ax4.scatter(trail_indices, intensities, c=elevations, cmap='terrain', s=1, alpha=0.6)
            ax4.set_xlabel('Trail Point Index')
            ax4.set_ylabel('LiDAR Intensity')
            ax4.set_title('LiDAR Intensity Along Trail')
            cbar4 = plt.colorbar(ax4.collections[0], ax=ax4)
            cbar4.set_label('Elevation (m)')
        else:
            ax4.text(0.5, 0.5, 'No intensity data available', 
                    transform=ax4.transAxes, ha='center', va='center')
            ax4.set_title('LiDAR Intensity (No Data)')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        # Calculate statistics
        stats = {
            'total_points': len(corridor_points),
            'elevation_range': (min(elevations), max(elevations)),
            'avg_elevation': np.mean(elevations),
            'vegetation_percentage': sum(1 for c in classifications if c in [3, 4, 5]) / len(classifications) * 100,
            'ground_percentage': sum(1 for c in classifications if c == 2) / len(classifications) * 100
        }
        
        return stats

# Main analysis function
def analyze_trail_with_lidar(gpx_file, lidar_folder):
    """Main function to analyze trail with LiDAR data"""
    analyzer = TrailLiDARAnalyzer(lidar_folder, gpx_file)
    
    # Load trail
    analyzer.load_gpx_trail()
    
    # Find relevant LiDAR files
    lidar_files = analyzer.find_relevant_lidar_files()
    
    if not lidar_files:
        print("No relevant LiDAR files found for this trail")
        return None
    
    print(f"Found {len(lidar_files)} relevant LiDAR files")
    
    # Load point clouds
    point_clouds = analyzer.extract_and_load_las_files(lidar_files)
    
    if not point_clouds:
        print("No point cloud data could be loaded")
        return None
    
    # Analyze corridor
    corridor_points = analyzer.analyze_trail_corridor()
    
    if corridor_points:
        # Create visualization
        stats = analyzer.create_lidar_visualization(corridor_points)
        return analyzer, stats
    else:
        print("No points found within trail corridor")
        return None

if __name__ == "__main__":
    # Example usage
    gpx_file = r"backend\data\43-mt-coot-tha-summit-track.gpx"
    lidar_folder = r"backend\data\QLD Government\Point Clouds\AHD"
    
    result = analyze_trail_with_lidar(gpx_file, lidar_folder)
    
    if result:
        analyzer, stats = result
        print("\nLiDAR Analysis Complete!")
        print(f"Statistics: {stats}")
