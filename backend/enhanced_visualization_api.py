"""
Enhanced trail visualization API endpoints for DEM and LiDAR data analysis
Add these endpoints to your existing main.py FastAPI application
"""

from fastapi import HTTPException
import numpy as np
from pathlib import Path
import os
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Import the analysis classes (you'll need to install required packages)
try:
    from .dem_trail_analysis import TrailDEMAnalyzer
    from .lidar_trail_analysis import TrailLiDARAnalyzer
except ImportError:
    print("DEM/LiDAR analysis modules not available. Install required packages: rasterio, laspy, geopandas")
    TrailDEMAnalyzer = None
    TrailLiDARAnalyzer = None

# Configuration
DEM_FOLDER = Path("backend/data/QLD Government/DEM/1 Metre")
LIDAR_FOLDER = Path("backend/data/QLD Government/Point Clouds/AHD")
GPX_FOLDER = Path("backend/data")

def encode_plot_to_base64():
    """Convert current matplotlib plot to base64 string"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plt.close()  # Close the plot to free memory
    
    encoded_plot = base64.b64encode(plot_data).decode('utf-8')
    return f"data:image/png;base64,{encoded_plot}"

# Add these endpoints to your existing FastAPI app in main.py:

@app.get("/trail/{trail_id}/dem-analysis")
async def get_trail_dem_analysis(trail_id: int):
    """Get DEM-based elevation analysis for a specific trail"""
    if TrailDEMAnalyzer is None:
        raise HTTPException(status_code=501, detail="DEM analysis not available. Missing required packages.")
    
    try:
        # Get trail from database
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        trail_name = trail.get("name", "Unknown Trail")
        
        # Create temporary GPX file from stored coordinates
        coordinates = trail.get("coordinates", [])
        if not coordinates:
            raise HTTPException(status_code=400, detail="Trail has no coordinate data")
        
        # Create GPX content
        gpx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="MAPENU" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>{trail_name}</name>
    <trkseg>
"""
        for coord in coordinates:
            lat, lon = coord
            gpx_content += f'      <trkpt lat="{lat}" lon="{lon}"><ele>0</ele></trkpt>\n'
        
        gpx_content += """    </trkseg>
  </trk>
</gpx>"""
        
        # Save temporary GPX file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            f.write(gpx_content)
            temp_gpx_path = f.name
        
        try:
            # Perform DEM analysis
            analyzer = TrailDEMAnalyzer(DEM_FOLDER, temp_gpx_path)
            dem_files = analyzer.find_relevant_dem_tiles()
            
            if not dem_files:
                return {
                    "success": False,
                    "message": "No DEM data available for this trail location",
                    "trail_name": trail_name
                }
            
            # Extract elevation profile
            elevation_data = analyzer.extract_elevation_profile(dem_files)
            valid_data = [p for p in elevation_data if not np.isnan(p['elevation'])]
            
            if not valid_data:
                return {
                    "success": False,
                    "message": "No valid elevation data could be extracted",
                    "trail_name": trail_name
                }
            
            # Generate visualization and get stats
            stats = analyzer.create_elevation_visualization()
            plot_base64 = encode_plot_to_base64()
            
            # Prepare detailed elevation profile data
            elevation_profile = []
            total_distance = 0
            
            for i, point in enumerate(valid_data):
                if i > 0:
                    prev_point = valid_data[i-1]
                    lat1, lon1 = prev_point['latitude'], prev_point['longitude']
                    lat2, lon2 = point['latitude'], point['longitude']
                    
                    # Calculate distance increment
                    dist_increment = haversine(lat1, lon1, lat2, lon2) / 1000  # km
                    total_distance += dist_increment
                
                elevation_profile.append({
                    "distance": round(total_distance, 3),
                    "elevation": round(point['elevation'], 1),
                    "latitude": point['latitude'],
                    "longitude": point['longitude']
                })
            
            return {
                "success": True,
                "trail_name": trail_name,
                "trail_id": trail_id,
                "analysis_type": "DEM",
                "statistics": stats,
                "elevation_profile": elevation_profile,
                "visualization": plot_base64,
                "data_sources": [Path(f).name for f in dem_files],
                "total_points": len(valid_data)
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_gpx_path)
            except:
                pass
                
    except Exception as e:
        print(f"DEM analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trail/{trail_id}/lidar-analysis")
async def get_trail_lidar_analysis(trail_id: int):
    """Get LiDAR point cloud analysis for a specific trail"""
    if TrailLiDARAnalyzer is None:
        raise HTTPException(status_code=501, detail="LiDAR analysis not available. Missing required packages.")
    
    try:
        # Get trail from database
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        trail_name = trail.get("name", "Unknown Trail")
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            raise HTTPException(status_code=400, detail="Trail has no coordinate data")
        
        # Create temporary GPX file
        gpx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="MAPENU" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>{trail_name}</name>
    <trkseg>
"""
        for coord in coordinates:
            lat, lon = coord
            gpx_content += f'      <trkpt lat="{lat}" lon="{lon}"><ele>0</ele></trkpt>\n'
        
        gpx_content += """    </trkseg>
  </trk>
</gpx>"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            f.write(gpx_content)
            temp_gpx_path = f.name
        
        try:
            # Perform LiDAR analysis
            analyzer = TrailLiDARAnalyzer(LIDAR_FOLDER, temp_gpx_path)
            analyzer.load_gpx_trail()
            
            lidar_files = analyzer.find_relevant_lidar_files()
            
            if not lidar_files:
                return {
                    "success": False,
                    "message": "No LiDAR data available for this trail location",
                    "trail_name": trail_name
                }
            
            # Load point clouds (limit to prevent memory issues)
            point_clouds = analyzer.extract_and_load_las_files(lidar_files[:2])  # Limit to 2 files
            
            if not point_clouds:
                return {
                    "success": False,
                    "message": "No point cloud data could be loaded",
                    "trail_name": trail_name
                }
            
            # Analyze corridor
            corridor_points = analyzer.analyze_trail_corridor(corridor_width=30)  # 30m corridor
            
            if not corridor_points:
                return {
                    "success": False,
                    "message": "No LiDAR points found within trail corridor",
                    "trail_name": trail_name
                }
            
            # Generate visualization and stats
            stats = analyzer.create_lidar_visualization(corridor_points)
            plot_base64 = encode_plot_to_base64()
            
            # Prepare vegetation analysis
            classifications = [p['classification'] for p in corridor_points]
            vegetation_analysis = {
                "ground_points": sum(1 for c in classifications if c == 2),
                "low_vegetation": sum(1 for c in classifications if c == 3),
                "medium_vegetation": sum(1 for c in classifications if c == 4),
                "high_vegetation": sum(1 for c in classifications if c == 5),
                "building_points": sum(1 for c in classifications if c == 6),
                "water_points": sum(1 for c in classifications if c == 9),
                "total_points": len(corridor_points)
            }
            
            return {
                "success": True,
                "trail_name": trail_name,
                "trail_id": trail_id,
                "analysis_type": "LiDAR",
                "statistics": stats,
                "vegetation_analysis": vegetation_analysis,
                "visualization": plot_base64,
                "data_sources": [pc['filename'] for pc in point_clouds],
                "corridor_width_meters": 30,
                "total_lidar_points": len(corridor_points)
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_gpx_path)
            except:
                pass
                
    except Exception as e:
        print(f"LiDAR analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trail/{trail_id}/combined-analysis")
async def get_trail_combined_analysis(trail_id: int):
    """Get combined DEM and LiDAR analysis for comprehensive trail visualization"""
    try:
        # Run both analyses
        dem_result = None
        lidar_result = None
        
        try:
            dem_response = await get_trail_dem_analysis(trail_id)
            if dem_response.get("success"):
                dem_result = dem_response
        except:
            pass
        
        try:
            lidar_response = await get_trail_lidar_analysis(trail_id)
            if lidar_response.get("success"):
                lidar_result = lidar_response
        except:
            pass
        
        # Get trail info
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        trail = trail_response.data[0] if trail_response.data else {}
        
        return {
            "success": True,
            "trail_id": trail_id,
            "trail_name": trail.get("name", "Unknown Trail"),
            "dem_analysis": dem_result,
            "lidar_analysis": lidar_result,
            "analysis_summary": {
                "dem_available": dem_result is not None,
                "lidar_available": lidar_result is not None,
                "total_data_sources": (
                    len(dem_result.get("data_sources", [])) if dem_result else 0
                ) + (
                    len(lidar_result.get("data_sources", [])) if lidar_result else 0
                )
            }
        }
        
    except Exception as e:
        print(f"Combined analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data-coverage")
async def get_data_coverage():
    """Get information about available DEM and LiDAR data coverage"""
    try:
        coverage_info = {
            "dem_tiles": [],
            "lidar_tiles": [],
            "coverage_area": {
                "min_lat": None,
                "max_lat": None,
                "min_lon": None,
                "max_lon": None
            }
        }
        
        # Scan DEM files
        if DEM_FOLDER.exists():
            dem_files = list(DEM_FOLDER.glob("**/*.tif"))
            for dem_file in dem_files[:50]:  # Limit for performance
                try:
                    # Parse coordinates from filename
                    # Format: Brisbane_YYYY_LGA_SW_XXXXXX_YYYYYYY_1K_DEM_1m.tif
                    parts = dem_file.stem.split('_')
                    if len(parts) >= 7:
                        easting = int(parts[-4])
                        northing = int(parts[-3])
                        year = parts[1]
                        
                        # Rough UTM to lat/lon conversion for display
                        lon = (easting - 500000) / 111000 + 153.0
                        lat = northing / 111000 - 27.0
                        
                        coverage_info["dem_tiles"].append({
                            "filename": dem_file.name,
                            "year": year,
                            "easting": easting,
                            "northing": northing,
                            "approximate_lat": round(lat, 4),
                            "approximate_lon": round(lon, 4)
                        })
                except:
                    continue
        
        # Scan LiDAR files
        if LIDAR_FOLDER.exists():
            lidar_files = list(LIDAR_FOLDER.glob("**/*.zip"))
            for lidar_file in lidar_files[:50]:  # Limit for performance
                try:
                    parts = lidar_file.stem.split('_')
                    if len(parts) >= 7:
                        easting = int(parts[-4])
                        northing = int(parts[-3])
                        year = parts[1]
                        
                        lon = (easting - 500000) / 111000 + 153.0
                        lat = northing / 111000 - 27.0
                        
                        coverage_info["lidar_tiles"].append({
                            "filename": lidar_file.name,
                            "year": year,
                            "easting": easting,
                            "northing": northing,
                            "approximate_lat": round(lat, 4),
                            "approximate_lon": round(lon, 4)
                        })
                except:
                    continue
        
        # Calculate approximate coverage area
        all_lats = []
        all_lons = []
        
        for tile in coverage_info["dem_tiles"] + coverage_info["lidar_tiles"]:
            all_lats.append(tile["approximate_lat"])
            all_lons.append(tile["approximate_lon"])
        
        if all_lats:
            coverage_info["coverage_area"] = {
                "min_lat": min(all_lats),
                "max_lat": max(all_lats),
                "min_lon": min(all_lons),
                "max_lon": max(all_lons)
            }
        
        return {
            "success": True,
            "coverage_info": coverage_info,
            "summary": {
                "total_dem_tiles": len(coverage_info["dem_tiles"]),
                "total_lidar_tiles": len(coverage_info["lidar_tiles"]),
                "data_years": list(set([
                    tile["year"] for tile in coverage_info["dem_tiles"] + coverage_info["lidar_tiles"]
                    if tile.get("year")
                ]))
            }
        }
        
    except Exception as e:
        print(f"Data coverage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
