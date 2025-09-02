import rasterio
import numpy as np
import matplotlib.pyplot as plt
import gpxpy
from shapely.geometry import Point, LineString
import geopandas as gpd
from rasterio.mask import mask
from rasterio.transform import rowcol
import os
from pathlib import Path
import glob

class TrailDEMAnalyzer:
    def __init__(self, dem_folder_path, gpx_file_path):
        self.dem_folder = Path(dem_folder_path)
        self.gpx_file = Path(gpx_file_path)
        self.trail_coords = []
        self.elevation_profile = []
        
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
    
    def find_relevant_dem_tiles(self):
        """Find DEM tiles that intersect with the trail"""
        if not self.trail_coords:
            self.load_gpx_trail()
        
        # Get trail bounds
        lons = [coord[0] for coord in self.trail_coords]
        lats = [coord[1] for coord in self.trail_coords]
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)
        
        print(f"Trail bounds: {min_lon:.6f}, {min_lat:.6f} to {max_lon:.6f}, {max_lat:.6f}")
        
        # Find DEM files in the folder
        dem_files = glob.glob(str(self.dem_folder / "**/*.tif"), recursive=True)
        relevant_dems = []
        
        for dem_file in dem_files:
            try:
                with rasterio.open(dem_file) as src:
                    bounds = src.bounds
                    # Check if DEM tile intersects with trail bounds
                    if (bounds.left <= max_lon and bounds.right >= min_lon and
                        bounds.bottom <= max_lat and bounds.top >= min_lat):
                        relevant_dems.append(dem_file)
                        print(f"Found relevant DEM: {Path(dem_file).name}")
            except Exception as e:
                print(f"Error reading {dem_file}: {e}")
                
        return relevant_dems
    
    def extract_elevation_profile(self, dem_files):
        """Extract elevation values along the trail path"""
        if not self.trail_coords:
            self.load_gpx_trail()
        
        elevation_data = []
        
        for i, coord in enumerate(self.trail_coords):
            lon, lat = coord
            elevation = None
            
            # Try each DEM file to find elevation at this point
            for dem_file in dem_files:
                try:
                    with rasterio.open(dem_file) as src:
                        bounds = src.bounds
                        if (bounds.left <= lon <= bounds.right and 
                            bounds.bottom <= lat <= bounds.top):
                            
                            # Convert lat/lon to pixel coordinates
                            row, col = rowcol(src.transform, lon, lat)
                            
                            # Check if coordinates are within the raster
                            if 0 <= row < src.height and 0 <= col < src.width:
                                elevation = src.read(1)[row, col]
                                if elevation != src.nodata:
                                    break
                except Exception as e:
                    continue
            
            elevation_data.append({
                'point_index': i,
                'longitude': lon,
                'latitude': lat,
                'elevation': elevation if elevation is not None else np.nan
            })
            
            if i % 100 == 0:  # Progress indicator
                print(f"Processed {i}/{len(self.trail_coords)} points")
        
        self.elevation_profile = elevation_data
        return elevation_data
    
    def create_elevation_visualization(self, output_path="trail_elevation_analysis.png"):
        """Create comprehensive elevation visualizations"""
        if not self.elevation_profile:
            print("No elevation data available. Run extract_elevation_profile first.")
            return
        
        # Filter out NaN values
        valid_data = [p for p in self.elevation_profile if not np.isnan(p['elevation'])]
        
        if not valid_data:
            print("No valid elevation data found")
            return
        
        distances = []
        elevations = [p['elevation'] for p in valid_data]
        
        # Calculate cumulative distance
        total_distance = 0
        distances.append(0)
        
        for i in range(1, len(valid_data)):
            lat1, lon1 = valid_data[i-1]['latitude'], valid_data[i-1]['longitude']
            lat2, lon2 = valid_data[i]['latitude'], valid_data[i]['longitude']
            
            # Haversine distance calculation
            from math import radians, sin, cos, sqrt, atan2
            R = 6371000  # Earth radius in meters
            
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            total_distance += distance
            distances.append(total_distance / 1000)  # Convert to kilometers
        
        # Create comprehensive visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Elevation Profile
        ax1.plot(distances, elevations, 'b-', linewidth=2)
        ax1.fill_between(distances, elevations, alpha=0.3, color='lightblue')
        ax1.set_xlabel('Distance (km)')
        ax1.set_ylabel('Elevation (m)')
        ax1.set_title('Trail Elevation Profile')
        ax1.grid(True, alpha=0.3)
        
        # 2. Elevation Statistics
        min_elev, max_elev = min(elevations), max(elevations)
        elev_gain = sum(max(0, elevations[i] - elevations[i-1]) for i in range(1, len(elevations)))
        elev_loss = sum(max(0, elevations[i-1] - elevations[i]) for i in range(1, len(elevations)))
        
        stats_text = f"""Elevation Statistics:
Min: {min_elev:.1f}m
Max: {max_elev:.1f}m
Range: {max_elev - min_elev:.1f}m
Gain: {elev_gain:.1f}m
Loss: {elev_loss:.1f}m
Total Distance: {distances[-1]:.2f}km"""
        
        ax2.text(0.1, 0.9, stats_text, transform=ax2.transAxes, fontsize=10, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Trail Statistics')
        
        # 3. Gradient Analysis
        gradients = []
        for i in range(1, len(elevations)):
            dist_diff = (distances[i] - distances[i-1]) * 1000  # Convert to meters
            elev_diff = elevations[i] - elevations[i-1]
            if dist_diff > 0:
                gradient = (elev_diff / dist_diff) * 100
                gradients.append(gradient)
            else:
                gradients.append(0)
        
        if gradients:
            ax3.plot(distances[1:], gradients, 'r-', linewidth=1)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax3.set_xlabel('Distance (km)')
            ax3.set_ylabel('Gradient (%)')
            ax3.set_title('Trail Gradient Profile')
            ax3.grid(True, alpha=0.3)
        
        # 4. 3D Trail Visualization (if possible)
        ax4.remove()
        ax4 = fig.add_subplot(2, 2, 4, projection='3d')
        
        lons = [p['longitude'] for p in valid_data]
        lats = [p['latitude'] for p in valid_data]
        
        ax4.plot(lons, lats, elevations, 'b-', linewidth=2)
        ax4.set_xlabel('Longitude')
        ax4.set_ylabel('Latitude')
        ax4.set_zlabel('Elevation (m)')
        ax4.set_title('3D Trail Visualization')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return {
            'min_elevation': min_elev,
            'max_elevation': max_elev,
            'elevation_gain': elev_gain,
            'elevation_loss': elev_loss,
            'total_distance': distances[-1],
            'max_gradient': max(gradients) if gradients else 0,
            'min_gradient': min(gradients) if gradients else 0
        }

# Example usage
def analyze_trail_with_dem(gpx_file, dem_folder):
    """Main function to analyze a trail with DEM data"""
    analyzer = TrailDEMAnalyzer(dem_folder, gpx_file)
    
    # Find relevant DEM tiles
    dem_files = analyzer.find_relevant_dem_tiles()
    
    if not dem_files:
        print("No relevant DEM files found for this trail")
        return None
    
    print(f"Found {len(dem_files)} relevant DEM files")
    
    # Extract elevation profile
    elevation_data = analyzer.extract_elevation_profile(dem_files)
    
    # Create visualization
    stats = analyzer.create_elevation_visualization()
    
    return analyzer, stats

if __name__ == "__main__":
    # Example usage with your data
    gpx_file = r"backend\data\43-mt-coot-tha-summit-track.gpx"
    dem_folder = r"backend\data\QLD Government\DEM\1 Metre"
    
    analyzer, stats = analyze_trail_with_dem(gpx_file, dem_folder)
    
    if stats:
        print("\nTrail Analysis Complete!")
        print(f"Statistics: {stats}")
