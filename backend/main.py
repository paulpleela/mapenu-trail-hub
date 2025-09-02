from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import gpxpy
import folium
from folium.plugins import Fullscreen, MeasureControl
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import math
import os
import tempfile
import uuid
import uvicorn
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import real DEM analysis
try:
    from real_dem_analysis import RealDEMAnalyzer
    dem_path = "data/QLD Government/DEM/1 Metre"
    dem_analyzer = RealDEMAnalyzer(dem_path)
    print(f"DEM Analyzer initialized with {len(dem_analyzer.dem_files)} DEM files")
except ImportError as e:
    print(f"DEM analysis not available: {e}")
    dem_analyzer = None
except Exception as e:
    print(f"DEM initialization error: {e}")
    dem_analyzer = None

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise Exception("Missing Supabase credentials. Please check your .env file.")

supabase: Client = create_client(supabase_url, supabase_key)


# Use the same haversine function from main.py
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def analyze_rolling_hills(elevations, distances):
    """Advanced rolling hills analysis: counts and scores significant ascents/descents"""
    if len(elevations) < 3:
        return 0.0

    threshold = 5  # meters, what counts as a 'hill'
    significant_changes = []
    for i in range(1, len(elevations)):
        change = elevations[i] - elevations[i - 1]
        if abs(change) >= threshold:
            significant_changes.append(abs(change))

    # Frequency: how many significant hills per km
    total_distance = distances[-1] if distances else 1
    hills_per_km = len(significant_changes) / total_distance if total_distance > 0 else 0

    # Amplitude: average size of significant hills
    avg_hill_size = sum(significant_changes) / len(significant_changes) if significant_changes else 0

    # Composite index: weighted sum (tweak weights as needed)
    rolling_index = 0.6 * hills_per_km + 0.4 * (avg_hill_size / 20)

    # Normalize to 0-1 scale
    normalized_index = min(rolling_index, 1.0)
    return normalized_index


def calculate_trail_similarity(trail1, trail2):
    """Calculate similarity score between two trails (0-1, higher = more similar)"""
    # Normalize factors for comparison
    distance_diff = abs(trail1['distance'] - trail2['distance'])
    distance_similarity = max(0, 1 - (distance_diff / 10))  # Within 10km is very similar
    
    elevation_gain_diff = abs(trail1['elevation_gain'] - trail2['elevation_gain'])
    elevation_similarity = max(0, 1 - (elevation_gain_diff / 500))  # Within 500m is similar
    
    difficulty_diff = abs(trail1['difficulty_score'] - trail2['difficulty_score'])
    difficulty_similarity = max(0, 1 - (difficulty_diff / 5))  # Within 5 points is similar
    
    rolling_hills_diff = abs(trail1['rolling_hills_index'] - trail2['rolling_hills_index'])
    rolling_similarity = max(0, 1 - (rolling_hills_diff / 0.5))  # Within 0.5 is similar
    
    # Weighted average (adjust weights as needed)
    similarity = (
        distance_similarity * 0.3 +
        elevation_similarity * 0.3 +
        difficulty_similarity * 0.25 +
        rolling_similarity * 0.15
    )
    
    return similarity


def get_trail_weather_exposure(trail):
    """Calculate static weather exposure risk (doesn't change with weather)"""
    max_elev = trail.get('max_elevation', 0)
    
    # Return exposure level and explanation (static characteristics)
    if max_elev > 1500:
        return {
            "exposure_level": "High",
            "risk_factors": ["Rapid weather changes", "Snow/ice risk", "High wind exposure", "Temperature drops"]
        }
    elif max_elev > 1000:
        return {
            "exposure_level": "Moderate", 
            "risk_factors": ["Cooler temperatures", "Wind exposure", "Potential fog"]
        }
    elif max_elev > 500:
        return {
            "exposure_level": "Low-Moderate",
            "risk_factors": ["Slightly cooler temps", "Some wind exposure"]
        }
    else:
        return {
            "exposure_level": "Low",
            "risk_factors": ["Minimal weather impact", "Protected terrain"]
        }


async def get_live_weather_difficulty(trail_coords, weather_api_key=None):
    """Get current weather conditions and calculate live difficulty multiplier"""
    if not trail_coords:
        return {
            "multiplier": 1.0,
            "conditions": "No coordinates available",
            "explanation": "Trail coordinates required for weather data"
        }
    
    # For demo purposes, simulate different conditions
    # In production, this would call OpenWeatherMap or similar API
    import random
    
    # Simulate current conditions (in real app, call weather API)
    conditions = random.choice([
        {"temp": 15, "wind": 10, "rain": False, "visibility": "Good"},
        {"temp": 5, "wind": 25, "rain": True, "visibility": "Poor"},
        {"temp": 25, "wind": 5, "rain": False, "visibility": "Excellent"},
        {"temp": -2, "wind": 30, "rain": False, "visibility": "Fair"},
        {"temp": 18, "wind": 15, "rain": False, "visibility": "Good"},
        {"temp": 12, "wind": 8, "rain": False, "visibility": "Excellent"}
    ])
    
    multiplier = 1.0
    factors = []
    
    # Temperature impact
    if conditions["temp"] < 0:
        multiplier += 0.3
        factors.append("Freezing temperatures")
    elif conditions["temp"] < 5:
        multiplier += 0.2
        factors.append("Cold temperatures")
    elif conditions["temp"] > 30:
        multiplier += 0.1
        factors.append("Hot temperatures")
    
    # Wind impact
    if conditions["wind"] > 25:
        multiplier += 0.2
        factors.append("Strong winds")
    elif conditions["wind"] > 15:
        multiplier += 0.1
        factors.append("Moderate winds")
    
    # Rain impact
    if conditions["rain"]:
        multiplier += 0.3
        factors.append("Wet/slippery conditions")
    
    # Visibility impact
    if conditions["visibility"] == "Poor":
        multiplier += 0.2
        factors.append("Poor visibility")
    
    condition_desc = f"{conditions['temp']}°C, {conditions['wind']}km/h winds"
    if conditions["rain"]:
        condition_desc += ", raining"
    
    return {
        "multiplier": round(multiplier, 2),
        "conditions": condition_desc,
        "explanation": f"Weather factors: {', '.join(factors) if factors else 'Good conditions'}"
    }


def calculate_terrain_variety(elevations):
    """Calculate how varied the terrain is (0-10 scale)"""
    if len(elevations) < 10:
        return 0
    
    # Calculate elevation ranges in 100m bands
    elevation_bands = set()
    for elev in elevations:
        band = int(elev / 100) * 100  # Round to nearest 100m
        elevation_bands.add(band)
    
    # More bands = more variety
    variety_score = min(len(elevation_bands), 10)  # Cap at 10
    
    # Also consider elevation change rate
    elevation_changes = []
    for i in range(1, len(elevations)):
        change_rate = abs(elevations[i] - elevations[i-1])
        elevation_changes.append(change_rate)
    
    # Bonus for frequent elevation changes
    if elevation_changes:
        avg_change = sum(elevation_changes) / len(elevation_changes)
        if avg_change > 20:  # Frequent significant changes
            variety_score = min(variety_score + 2, 10)
        elif avg_change > 10:  # Moderate changes
            variety_score = min(variety_score + 1, 10)
    
    return variety_score


def get_terrain_variety_description(score):
    """Get a description for terrain variety score"""
    if score >= 8:
        return "Highly varied terrain with multiple elevation zones"
    elif score >= 6:
        return "Good terrain variety with several elevation changes"
    elif score >= 4:
        return "Moderate terrain variety with some elevation changes"
    elif score >= 2:
        return "Limited terrain variety, mostly consistent elevation"
    else:
        return "Flat or very consistent terrain"


def get_weather_exposure_from_score(score):
    """Convert weather score back to exposure level and risk factors"""
    # Handle None/null values
    if score is None:
        score = 1.0  # Default to low exposure
    
    try:
        score = float(score)  # Ensure it's a number
    except (ValueError, TypeError):
        score = 1.0  # Default to low exposure if conversion fails
    
    if score >= 1.25:
        return {
            "exposure_level": "High",
            "risk_factors": ["Rapid weather changes", "Snow/ice risk", "High wind exposure", "Temperature drops"]
        }
    elif score >= 1.15:
        return {
            "exposure_level": "Moderate",
            "risk_factors": ["Cooler temperatures", "Wind exposure", "Potential fog"]
        }
    elif score >= 1.05:
        return {
            "exposure_level": "Low-Moderate",
            "risk_factors": ["Slightly cooler temps", "Some wind exposure"]
        }
    else:
        return {
            "exposure_level": "Low",
            "risk_factors": ["Minimal weather impact", "Protected terrain"]
        }


@app.get("/trails")
async def get_trails():
    """Get all trails from Supabase database"""
    try:
        response = supabase.table("trails").select("*").execute()
        trails = response.data
        return {"success": True, "trails": trails}
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trail/{trail_id}/similar")
async def get_similar_trails(trail_id: int, limit: int = 5):
    """Get trails similar to the specified trail"""
    try:
        # Get the target trail
        target_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not target_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        target_trail = target_response.data[0]
        
        # Get all other trails
        all_trails_response = supabase.table("trails").select("*").neq("id", trail_id).execute()
        all_trails = all_trails_response.data
        
        # Calculate similarity scores
        similarities = []
        for trail in all_trails:
            similarity_score = calculate_trail_similarity(target_trail, trail)
            similarities.append({
                "trail": trail,
                "similarity_score": similarity_score
            })
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        similar_trails = similarities[:limit]
        
        return {
            "success": True,
            "target_trail": target_trail["name"],
            "similar_trails": similar_trails
        }
        
    except Exception as e:
        print(f"Similar trails error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/overview")
async def get_analytics_overview():
    """Get overall analytics for all trails"""
    try:
        response = supabase.table("trails").select("*").execute()
        trails = response.data
        
        if not trails:
            return {"success": True, "analytics": {"total_trails": 0}}
        
        # Calculate aggregate statistics
        total_distance = sum(trail.get('distance', 0) for trail in trails)
        total_elevation_gain = sum(trail.get('elevation_gain', 0) for trail in trails)
        avg_difficulty = sum(trail.get('difficulty_score', 0) for trail in trails) / len(trails)
        
        # Difficulty distribution
        difficulty_dist = {"Easy": 0, "Moderate": 0, "Hard": 0, "Extreme": 0}
        for trail in trails:
            level = trail.get('difficulty_level', 'Unknown')
            if level in difficulty_dist:
                difficulty_dist[level] += 1
        
        # Distance categories
        distance_categories = {"Short (<5km)": 0, "Medium (5-15km)": 0, "Long (>15km)": 0}
        for trail in trails:
            distance = trail.get('distance', 0)
            if distance < 5:
                distance_categories["Short (<5km)"] += 1
            elif distance <= 15:
                distance_categories["Medium (5-15km)"] += 1
            else:
                distance_categories["Long (>15km)"] += 1
        
        return {
            "success": True,
            "analytics": {
                "total_trails": len(trails),
                "total_distance_km": round(total_distance, 1),
                "total_elevation_gain_m": round(total_elevation_gain, 0),
                "avg_difficulty_score": round(avg_difficulty, 1),
                "difficulty_distribution": difficulty_dist,
                "distance_categories": distance_categories,
                "most_challenging": max(trails, key=lambda t: t.get('difficulty_score', 0))['name'],
                "longest_trail": max(trails, key=lambda t: t.get('distance', 0))['name']
            }
        }
        
    except Exception as e:
        print(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trail/{trail_id}/weather")
async def get_trail_weather(trail_id: int):
    """Get live weather conditions and difficulty multiplier for a trail"""
    try:
        print(f"Getting weather data for trail ID: {trail_id}")
        
        # Get the trail
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        print(f"Found trail: {trail.get('name', 'Unknown')}")
        
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            raise HTTPException(status_code=400, detail="Trail has no coordinate data")
        
        # Get midpoint coordinates for weather lookup
        mid_index = len(coordinates) // 2
        trail_coords = coordinates[mid_index]
        print(f"Using coordinates: {trail_coords}")
        
        # Get live weather data (this would use a real weather API in production)
        weather_data = await get_live_weather_difficulty(trail_coords)
        print(f"Weather data: {weather_data}")
        
        # Get static weather exposure info from stored score
        weather_score = trail.get("weather_difficulty_multiplier")
        if weather_score is None:
            weather_score = 1.0  # Default value
        weather_exposure = get_weather_exposure_from_score(weather_score)
        
        # Safe difficulty calculation
        base_difficulty = trail.get("difficulty_score", 0)
        if base_difficulty is None:
            base_difficulty = 0
        
        weather_multiplier = weather_data.get("multiplier", 1.0)
        if weather_multiplier is None:
            weather_multiplier = 1.0
        
        result = {
            "success": True,
            "trail_name": trail.get("name", "Unknown Trail"),
            "live_weather": weather_data,
            "weather_exposure": weather_exposure,
            "coordinates": trail_coords,
            "updated_difficulty": {
                "base_difficulty": base_difficulty,
                "weather_adjusted": round(base_difficulty * weather_multiplier, 1),
                "adjustment_explanation": f"Difficulty adjusted by {weather_multiplier}x due to current conditions"
            }
        }
        
        print(f"Returning result: {result}")
        return result
        
    except Exception as e:
        print(f"Weather lookup error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/map")
async def get_map():
    """Generate map with all trails from Supabase"""
    try:
        # Get trails from database
        response = supabase.table("trails").select("*").execute()
        trails = response.data

        # If no trails, return empty map
        if not trails:
            # Create empty map centered on Brisbane
            m = folium.Map(location=[-27.4698, 152.9560], zoom_start=12)

            # Generate unique filename
            map_id = str(uuid.uuid4())
            map_filename = f"empty_map_{map_id}.html"
            map_path = os.path.join(tempfile.gettempdir(), map_filename)

            # Save map to temporary file
            m.save(map_path)

            return {
                "success": True,
                "map_url": f"/maps/{map_filename}",
                "trails_count": 0,
                "message": "No trails available. Upload GPX files to get started.",
            }

        # Create a map centered on Brisbane for multiple trails
        m = folium.Map(
            location=[-27.4698, 152.9560], 
            zoom_start=12,
            tiles='OpenStreetMap',  # Better base layer
            control_scale=True,     # Add scale control
            prefer_canvas=False     # Ensure interactive behavior
        )

        # Collect all coordinates to calculate bounds
        all_coordinates = []
        
        # Color palette for different trails
        colors = ["blue", "red", "green", "purple", "orange", "darkred", "lightred"]

        for i, trail in enumerate(trails):
            color = colors[i % len(colors)]
            coordinates = trail.get("coordinates", [])

            if coordinates:
                # Add all coordinates to bounds calculation
                all_coordinates.extend(coordinates)
                
                # Add polyline for this trail with better styling
                folium.PolyLine(
                    coordinates,
                    color=color,
                    weight=4,
                    opacity=0.8,
                    tooltip=f"{trail.get('name', 'Unnamed Trail')} - {trail.get('distance', 0):.1f}km",
                    popup=folium.Popup(
                        f"""
                        <div style="font-family: Arial, sans-serif;">
                            <h4 style="margin: 0 0 10px 0; color: {color};">{trail.get('name', 'Unnamed Trail')}</h4>
                            <p style="margin: 5px 0;"><strong>Distance:</strong> {trail.get('distance', 0):.1f} km</p>
                            <p style="margin: 5px 0;"><strong>Elevation Gain:</strong> {trail.get('elevation_gain', 0)} m</p>
                            <p style="margin: 5px 0;"><strong>Difficulty:</strong> {trail.get('difficulty_level', 'Unknown')}</p>
                            <p style="margin: 5px 0;"><strong>Max Elevation:</strong> {trail.get('max_elevation', 0)} m</p>
                        </div>
                        """,
                        max_width=250
                    )
                ).add_to(m)

                # Add start marker with better styling
                start_coord = coordinates[0]
                folium.Marker(
                    start_coord,
                    popup=folium.Popup(f"<strong>Start:</strong> {trail.get('name', 'Unnamed Trail')}", max_width=200),
                    tooltip="Trail Start",
                    icon=folium.Icon(color="green", icon="play", prefix="fa")
                ).add_to(m)

                # Add end marker with better styling
                end_coord = coordinates[-1]
                folium.Marker(
                    end_coord,
                    popup=folium.Popup(f"<strong>End:</strong> {trail.get('name', 'Unnamed Trail')}", max_width=200),
                    tooltip="Trail End",
                    icon=folium.Icon(color="red", icon="stop", prefix="fa")
                ).add_to(m)

        # Fit map bounds to show all trails
        if all_coordinates:
            # Calculate bounds
            lats = [coord[0] for coord in all_coordinates]
            lons = [coord[1] for coord in all_coordinates]
            
            # Add some padding to the bounds
            lat_padding = (max(lats) - min(lats)) * 0.1
            lon_padding = (max(lons) - min(lons)) * 0.1
            
            bounds = [
                [min(lats) - lat_padding, min(lons) - lon_padding],
                [max(lats) + lat_padding, max(lons) + lon_padding]
            ]
            
            m.fit_bounds(bounds)
        
        # Add layer control for different map views
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer(
            'Stamen Terrain', 
            name='Terrain',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
        ).add_to(m)
        folium.TileLayer(
            'CartoDB positron', 
            name='Light',
            attr='&copy; OpenStreetMap contributors &copy; CARTO'
        ).add_to(m)
        folium.LayerControl().add_to(m)
        
        # Add fullscreen control
        Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(m)
        
        # Add measure control for distance measurements
        MeasureControl(primary_length_unit="kilometers").add_to(m)

        # Add JavaScript for trail click handling
        trail_data_js = f"""
        var allTrailsData = {json.dumps([{
            'id': trail.get('id'),
            'name': trail.get('name', 'Unnamed Trail'),
            'distance': trail.get('distance', 0),
            'elevationGain': trail.get('elevation_gain', 0),
            'elevationLoss': trail.get('elevation_loss', 0),
            'maxElevation': trail.get('max_elevation', 0),
            'minElevation': trail.get('min_elevation', 0),
            'rollingHillsIndex': trail.get('rolling_hills_index', 0),
            'difficultyScore': trail.get('difficulty_score', 0),
            'difficultyLevel': trail.get('difficulty_level', 'Unknown'),
            'elevationProfile': trail.get('elevation_profile', []),
            'coordinates': trail.get('coordinates', [])
        } for trail in trails])};
        
        console.log('Trail data available:', allTrailsData.length, 'trails');
        allTrailsData.forEach(function(trail, index) {{
            console.log('Trail', index + ':', trail.name, '- ID:', trail.id);
        }});
        
        function sendTrailDataToParent(trailData) {{
            console.log('Sending trail data to parent:', trailData);
            if (window.parent && window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'trail-clicked',
                    data: trailData
                }}, '*');
            }} else {{
                console.log('No parent window found - running in standalone mode');
            }}
        }}
        
        function setupClickHandlers() {{
            var polylines = document.querySelectorAll('.leaflet-interactive');
            console.log('Found', polylines.length, 'interactive elements');
            
            polylines.forEach(function(polyline, index) {{
                polyline.style.cursor = 'pointer';
                polyline.addEventListener('click', function(e) {{
                    console.log('Polyline', index, 'clicked');
                    if (allTrailsData[index]) {{
                        sendTrailDataToParent(allTrailsData[index]);
                    }} else {{
                        console.log('No trail data found for index', index);
                    }}
                }});
            }});
        }}
        
        // Setup click handlers when DOM is ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(setupClickHandlers, 1000);
            }});
        }} else {{
            setTimeout(setupClickHandlers, 1000);
        }}
        """

        # Add JavaScript to the map
        m.get_root().html.add_child(
            folium.Element(
                f"""
        <script>
        {trail_data_js}
        </script>
        """
            )
        )

        # Generate unique filename and save map
        map_id = str(uuid.uuid4())
        map_filename = f"trails_map_{map_id}.html"
        map_path = os.path.join(tempfile.gettempdir(), map_filename)

        # Save map to temporary file
        m.save(map_path)

        return {
            "success": True,
            "map_url": f"/maps/{map_filename}",
            "trails_count": len(trails),
        }

    except Exception as e:
        print(f"Map generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-gpx")
async def upload_gpx(file: UploadFile = File(...)):
    """Handle GPX file upload and save to Supabase"""
    if not file.filename.lower().endswith(".gpx"):
        raise HTTPException(status_code=400, detail="File must be a GPX file")

    try:
        # Read GPX content
        content = await file.read()
        gpx_content = content.decode("utf-8")

        # Extract trail name from filename
        trail_name = file.filename.replace(".gpx", "").replace("_", " ").title()

        # Analyze trail data
        gpx = gpxpy.parse(gpx_content)
        coords = []
        elevations = []
        distances = [0]
        slopes = [0]  # Start with 0 slope for first point

        for track in gpx.tracks:
            for segment in track.segments:
                for i, point in enumerate(segment.points):
                    coords.append([point.latitude, point.longitude])
                    elevations.append(point.elevation or 0)

                    if i > 0:
                        prev_point = segment.points[i - 1]
                        dist = (
                            haversine(
                                prev_point.latitude,
                                prev_point.longitude,
                                point.latitude,
                                point.longitude,
                            )
                            / 1000
                        )
                        distances.append(distances[-1] + dist)

                        # Slope analysis (gradient in %)
                        elev_diff = (point.elevation or 0) - (prev_point.elevation or 0)
                        dist_m = haversine(
                            prev_point.latitude,
                            prev_point.longitude,
                            point.latitude,
                            point.longitude,
                        )
                        if dist_m > 0:
                            gradient = (elev_diff / dist_m) * 100
                            slopes.append(gradient)
                        else:
                            slopes.append(0)

        if not coords:
            raise HTTPException(
                status_code=400, detail="No track points found in GPX file"
            )

        # Calculate statistics
        total_distance = distances[-1] if len(distances) > 1 else 0
        elevation_gain = (
            sum(
                max(0, elevations[i] - elevations[i - 1])
                for i in range(1, len(elevations))
            )
            if len(elevations) > 1
            else 0
        )
        elevation_loss = (
            sum(
                max(0, elevations[i - 1] - elevations[i])
                for i in range(1, len(elevations))
            )
            if len(elevations) > 1
            else 0
        )
        max_elevation = max(elevations) if elevations else 0
        min_elevation = min(elevations) if elevations else 0

        # Rolling hills index (advanced)
        rolling_hills_index = round(analyze_rolling_hills(elevations, distances), 2)

        # Slope analysis
        if slopes and len(slopes) > 1:  # Skip first element (always 0)
            slope_values = slopes[1:]  # Skip the initial 0
            max_slope = max(slope_values) if slope_values else 0
            avg_slope = sum(map(abs, slope_values)) / len(slope_values) if slope_values else 0
        else:
            max_slope = 0
            avg_slope = 0

        # Segment analysis (500m segments)
        segment_length = 0.5  # km
        segments = []
        if len(distances) > 1:
            seg_start_idx = 0
            while seg_start_idx < len(distances) - 1:
                seg_end_idx = seg_start_idx
                # Find the end index for this segment
                while (seg_end_idx < len(distances) - 1 and
                       distances[seg_end_idx] - distances[seg_start_idx] < segment_length):
                    seg_end_idx += 1
                # Calculate stats for this segment
                seg_dist = distances[seg_end_idx] - distances[seg_start_idx]
                seg_elev_change = elevations[seg_end_idx] - elevations[seg_start_idx]
                # Slope for segment
                if seg_dist > 0:
                    seg_slope = (seg_elev_change / (seg_dist * 1000)) * 100
                else:
                    seg_slope = 0
                segments.append({
                    "start_distance": round(distances[seg_start_idx], 2),
                    "end_distance": round(distances[seg_end_idx], 2),
                    "elevation_change": round(seg_elev_change, 1),
                    "avg_slope": round(seg_slope, 2)
                })
                seg_start_idx = seg_end_idx

        # Simple difficulty calculation
        distance_factor = min(total_distance / 10, 1) * 3
        elevation_factor = min(elevation_gain / 1000, 1) * 4
        rolling_factor = rolling_hills_index * 3
        difficulty_score = distance_factor + elevation_factor + rolling_factor

        if difficulty_score <= 3:
            difficulty_level = "Easy"
        elif difficulty_score <= 6:
            difficulty_level = "Moderate"
        elif difficulty_score <= 8:
            difficulty_level = "Hard"
        else:
            difficulty_level = "Extreme"

        # Check for duplicate trails before inserting
        # First check by exact name match
        existing_trails_response = (
            supabase.table("trails").select("*").eq("name", trail_name).execute()
        )

        if existing_trails_response.data:
            raise HTTPException(
                status_code=409,
                detail=f"Trail with name '{trail_name}' already exists in database",
            )

        # Check for similar starting coordinates (within ~100m radius)
        # This prevents uploading the same trail with different names
        start_lat, start_lon = coords[0]
        all_trails_response = (
            supabase.table("trails").select("name, coordinates").execute()
        )

        for existing_trail in all_trails_response.data:
            if existing_trail.get("coordinates"):
                existing_start = existing_trail["coordinates"][0]
                existing_lat, existing_lon = existing_start

                # Calculate distance between starting points
                distance_between_starts = haversine(
                    start_lat, start_lon, existing_lat, existing_lon
                )

                # If starts are within 100 meters, likely duplicate
                if distance_between_starts < 100:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Trail starting near same location as existing trail '{existing_trail['name']}' (within 100m). Possible duplicate.",
                    )

        # Create new trail data for Supabase
        weather_exposure = get_trail_weather_exposure({"max_elevation": max_elevation})
        terrain_variety = calculate_terrain_variety(elevations)
        
        # Convert weather exposure to a numeric score for database compatibility
        exposure_scores = {"Low": 1.0, "Low-Moderate": 1.1, "Moderate": 1.2, "High": 1.3}
        weather_score = exposure_scores.get(weather_exposure["exposure_level"], 1.0)
        
        new_trail_data = {
            "name": trail_name,
            "distance": round(total_distance, 2),
            "elevation_gain": int(round(elevation_gain, 0)),
            "elevation_loss": int(round(elevation_loss, 0)),
            "max_elevation": int(round(max_elevation, 0)),
            "min_elevation": int(round(min_elevation, 0)),
            "rolling_hills_index": rolling_hills_index,
            "difficulty_score": round(difficulty_score, 1),
            "difficulty_level": difficulty_level,
            "coordinates": coords,
            "elevation_profile": [
                {
                    "distance": round(dist, 2), 
                    "elevation": round(ele, 1),
                    "slope": round(slopes[i] if i < len(slopes) else 0, 2)
                }
                for i, (dist, ele) in enumerate(zip(distances, elevations))
            ],
            "max_slope": round(max_slope, 2),
            "avg_slope": round(avg_slope, 2),
            "segments": segments,
            # Enhanced effort estimation using Naismith's Rule + terrain adjustments
            "estimated_time_hours": round((total_distance / 5) + (elevation_gain / 600) + (rolling_hills_index * 0.5), 2),
            # Improved analytics fields (using existing column names)
            "terrain_variety_score": terrain_variety,
            "elevation_change_total": int(round(elevation_gain + elevation_loss, 0)),
            # Store weather data in existing numeric fields, we'll interpret on frontend
            "weather_difficulty_multiplier": weather_score,  # Use existing column with new meaning
            "technical_rating": min(10, int(max_slope / 10 + rolling_hills_index * 5 + 1)),  # 1-10 technical difficulty
        }

        # Insert trail into Supabase database
        response = supabase.table("trails").insert(new_trail_data).execute()

        if response.data:
            inserted_trail = response.data[0]
            return {
                "success": True,
                "message": "Trail uploaded successfully to database",
                "trail": inserted_trail,
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to insert trail into database"
            )

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trail/{trail_id}/3d-terrain-viewer")
async def get_trail_3d_terrain_viewer(trail_id: int):
    """Serve interactive 3D terrain visualization as a standalone HTML page"""
    try:
        if not dem_analyzer:
            return JSONResponse({"error": "DEM analyzer not available"}, status_code=503)
        
        # Get trail data
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            return JSONResponse({"error": "Trail not found"}, status_code=404)
        
        trail = trail_response.data[0]
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            return JSONResponse({"error": "No coordinates available"}, status_code=400)
        
        # Generate 3D visualization
        visualization_result = dem_analyzer.create_3d_terrain_visualization(coordinates, buffer_meters=1000)
        
        if not visualization_result.get("success"):
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>3D Terrain Error</title></head>
            <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                <h2>3D Terrain Visualization Error</h2>
                <p>{visualization_result.get('error', 'Unknown error')}</p>
            </body>
            </html>
            """
            return HTMLResponse(content=error_html, status_code=500)
        
        # Return interactive HTML if available
        if visualization_result.get("type") == "interactive":
            return HTMLResponse(content=visualization_result["html_content"])
        else:
            # Create HTML wrapper for static image
            static_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>3D Terrain - {trail.get('name', 'Trail')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; text-align: center; }}
                    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }}
                </style>
            </head>
            <body>
                <h2>3D Terrain Visualization - {trail.get('name', 'Trail')}</h2>
                <img src="data:image/png;base64,{visualization_result['image_base64']}" 
                     alt="3D Terrain Visualization" />
                <p>{visualization_result['description']}</p>
            </body>
            </html>
            """
            return HTMLResponse(content=static_html)
    
    except Exception as e:
        print(f"3D terrain viewer error: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>3D Terrain Error</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
            <h2>3D Terrain Visualization Error</h2>
            <p>Server error: {str(e)}</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@app.get("/maps/{filename}")
async def serve_map_file(filename: str):
    """Serve generated map files"""
    map_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(map_path):
        raise HTTPException(status_code=404, detail="Map file not found")
    return FileResponse(map_path)


# Enhanced DEM/LiDAR Analysis Endpoints
@app.get("/trail/{trail_id}/dem-analysis")
async def get_trail_dem_analysis(trail_id: int):
    """Analyze DEM data for a specific trail using real DEM files"""
    try:
        if not dem_analyzer:
            return {"success": False, "error": "DEM analyzer not available. Check DEM file path and dependencies."}
        
        # Get trail data
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            return {"success": False, "error": "No coordinates available for this trail"}
        
        print(f"Analyzing trail '{trail.get('name')}' with {len(coordinates)} coordinate points")
        
        # Extract real elevation profile from DEM data
        elevation_analysis = dem_analyzer.extract_elevation_profile(coordinates)
        
        if not elevation_analysis.get("success"):
            return {"success": False, "error": elevation_analysis.get("error", "Analysis failed")}
        
        # Analyze terrain features
        terrain_features = dem_analyzer.analyze_terrain_features(coordinates)
        
        # Generate 3D visualization
        visualization_3d = dem_analyzer.create_3d_terrain_visualization(coordinates)
        
        result = {
            "success": True,
            "trail_name": trail.get("name"),
            "elevation_analysis": elevation_analysis,
            "terrain_features": terrain_features,
            "visualization_3d": visualization_3d,
            "data_quality": {
                "resolution": "1 meter",
                "data_source": "Queensland Government DEM",
                "coordinate_system": "GDA94 MGA Zone 56",
                "accuracy": "±0.5 meters"
            }
        }
        
        return result
    
    except Exception as e:
        print(f"DEM analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trail/{trail_id}/3d-terrain")
async def get_trail_3d_terrain(trail_id: int):
    """Generate interactive 3D terrain visualization for a trail"""
    try:
        if not dem_analyzer:
            return {"success": False, "error": "DEM analyzer not available"}
        
        # Get trail data
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            return {"success": False, "error": "No coordinates available"}
        
        # Generate 3D visualization
        visualization_result = dem_analyzer.create_3d_terrain_visualization(coordinates, buffer_meters=1000)
        
        if not visualization_result.get("success"):
            return {
                "success": False, 
                "error": visualization_result.get("error", "Failed to generate 3D visualization")
            }
        
        # Return based on visualization type
        if visualization_result.get("type") == "interactive":
            return {
                "success": True,
                "trail_name": trail.get("name"),
                "visualization_type": "interactive",
                "visualization_html": visualization_result["html_content"],
                "description": visualization_result["description"]
            }
        else:
            # Static visualization
            return {
                "success": True,
                "trail_name": trail.get("name"),
                "visualization_type": "static",
                "visualization": f"data:image/png;base64,{visualization_result['image_base64']}",
                "description": visualization_result["description"]
            }
    
    except Exception as e:
        print(f"3D terrain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trail/{trail_id}/dem-overlay-map")
async def get_trail_dem_overlay_map(trail_id: int):
    """Generate map with DEM elevation overlay for specific trail"""
    try:
        if not dem_analyzer:
            raise HTTPException(status_code=503, detail="DEM analyzer not available")
        
        # Get trail data
        trail_response = supabase.table("trails").select("*").eq("id", trail_id).execute()
        if not trail_response.data:
            raise HTTPException(status_code=404, detail="Trail not found")
        
        trail = trail_response.data[0]
        coordinates = trail.get("coordinates", [])
        
        if not coordinates:
            raise HTTPException(status_code=400, detail="No coordinates available")
        
        # Get DEM analysis
        elevation_analysis = dem_analyzer.extract_elevation_profile(coordinates)
        
        if not elevation_analysis.get("success"):
            # Create basic map without DEM overlay
            center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
            center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles='OpenStreetMap')
            
            # Add trail without elevation data
            folium.PolyLine(
                coordinates,
                color="blue",
                weight=4,
                opacity=0.8,
                tooltip=f"{trail.get('name')} - No DEM data available"
            ).add_to(m)
            
        else:
            # Create map with elevation overlay
            profile_coords = elevation_analysis["elevation_profile"]["coordinates"]
            elevations = elevation_analysis["elevation_profile"]["elevations"]
            
            center_lat = sum(coord[0] for coord in profile_coords) / len(profile_coords)
            center_lon = sum(coord[1] for coord in profile_coords) / len(profile_coords)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles='OpenStreetMap')
            
            # Create elevation-colored trail segments
            import matplotlib.cm as cm
            import matplotlib.colors as mcolors
            
            # Normalize elevations for color mapping
            norm = mcolors.Normalize(vmin=min(elevations), vmax=max(elevations))
            colormap = cm.terrain
            
            # Add trail segments with elevation-based colors
            for i in range(len(profile_coords) - 1):
                start_coord = profile_coords[i]
                end_coord = profile_coords[i + 1]
                elevation = elevations[i]
                
                # Get color based on elevation
                rgba_color = colormap(norm(elevation))
                hex_color = mcolors.to_hex(rgba_color)
                
                folium.PolyLine(
                    [start_coord, end_coord],
                    color=hex_color,
                    weight=6,
                    opacity=0.9,
                    tooltip=f"Elevation: {elevation:.1f}m"
                ).add_to(m)
            
            # Add elevation markers at key points
            max_elev_idx = elevations.index(max(elevations))
            min_elev_idx = elevations.index(min(elevations))
            
            # Highest point marker
            folium.Marker(
                profile_coords[max_elev_idx],
                popup=f"Highest Point: {max(elevations):.1f}m",
                tooltip="Trail High Point",
                icon=folium.Icon(color="red", icon="triangle-top", prefix="fa")
            ).add_to(m)
            
            # Lowest point marker
            folium.Marker(
                profile_coords[min_elev_idx],
                popup=f"Lowest Point: {min(elevations):.1f}m",
                tooltip="Trail Low Point",
                icon=folium.Icon(color="blue", icon="triangle-bottom", prefix="fa")
            ).add_to(m)
            
            # Add elevation legend
            legend_html = f'''
            <div style="position: fixed; 
                        bottom: 50px; right: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><b>Elevation</b></p>
            <p><i class="fa fa-triangle-top" style="color:red"></i> Max: {max(elevations):.1f}m</p>
            <p><i class="fa fa-triangle-bottom" style="color:blue"></i> Min: {min(elevations):.1f}m</p>
            <p>Trail colored by elevation</p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add terrain layer options
        folium.TileLayer(
            'Stamen Terrain', 
            name='Terrain',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
        ).add_to(m)
        folium.TileLayer(
            'CartoDB positron', 
            name='Light',
            attr='&copy; OpenStreetMap contributors &copy; CARTO'
        ).add_to(m)
        folium.LayerControl().add_to(m)
        
        # Add fullscreen and measure controls
        Fullscreen().add_to(m)
        MeasureControl(primary_length_unit="kilometers").add_to(m)
        
        # Fit bounds to trail
        if coordinates:
            lats = [coord[0] for coord in coordinates]
            lons = [coord[1] for coord in coordinates]
            padding = 0.001
            bounds = [
                [min(lats) - padding, min(lons) - padding],
                [max(lats) + padding, max(lons) + padding]
            ]
            m.fit_bounds(bounds)
        
        # Generate unique filename and save map
        map_id = str(uuid.uuid4())
        map_filename = f"trail_dem_{trail_id}_{map_id}.html"
        map_path = os.path.join(tempfile.gettempdir(), map_filename)
        
        m.save(map_path)
        
        return {
            "success": True,
            "map_url": f"/maps/{map_filename}",
            "trail_name": trail.get("name"),
            "has_dem_data": elevation_analysis.get("success", False)
        }
        
    except Exception as e:
        print(f"DEM overlay map error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/dem/coverage")
async def get_dem_coverage():
    """Get information about available DEM coverage"""
    try:
        if not dem_analyzer:
            return {
                "success": False,
                "error": "DEM analyzer not available",
                "troubleshooting": {
                    "check_path": "backend/data/QLD Government/DEM/1 Metre",
                    "required_packages": ["rasterio", "geopandas", "pyproj"],
                    "file_format": ".tif files"
                }
            }
        
        # Get actual file information
        dem_files = dem_analyzer.dem_files
        total_size_mb = 0
        
        file_info = []
        for dem_file in dem_files[:10]:  # Show first 10 files as examples
            try:
                size_mb = os.path.getsize(dem_file) / (1024 * 1024)
                total_size_mb += size_mb
                
                # Extract coordinate info from filename
                filename = os.path.basename(dem_file)
                file_info.append({
                    "filename": filename,
                    "size_mb": round(size_mb, 2),
                    "path": dem_file
                })
            except:
                continue
        
        # Estimate total size for all files
        if len(dem_files) > 10:
            avg_size = total_size_mb / len(file_info) if file_info else 50
            estimated_total_mb = avg_size * len(dem_files)
        else:
            estimated_total_mb = total_size_mb
        
        coverage_info = {
            "available": True,
            "total_files": len(dem_files),
            "resolution": "1 meter",
            "format": "GeoTIFF (.tif)",
            "coordinate_system": "GDA94 / MGA Zone 56 (EPSG:28356)",
            "coverage_area": "Brisbane Region",
            "years_available": ["2009", "2014", "2019"],
            "estimated_size_gb": round(estimated_total_mb / 1024, 2),
            "sample_files": file_info,
            "data_path": dem_analyzer.dem_base_path
        }
        
        return {"success": True, "coverage": coverage_info}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
