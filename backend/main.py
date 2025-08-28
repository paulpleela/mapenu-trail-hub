from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import gpxpy
import folium
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import math
import os
import tempfile
import uuid
import uvicorn
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
    """Analyze rolling hills characteristics"""
    if len(elevations) < 3:
        return 0.0

    # Calculate elevation changes
    elevation_changes = []
    for i in range(1, len(elevations)):
        change = abs(elevations[i] - elevations[i - 1])
        elevation_changes.append(change)

    # Calculate rolling hills index (average change per distance unit)
    total_distance = distances[-1] if distances else 1
    total_elevation_change = sum(elevation_changes)
    rolling_index = total_elevation_change / total_distance if total_distance > 0 else 0

    # Normalize to 0-1 scale (adjust based on your data)
    normalized_index = min(rolling_index / 100, 1.0)
    return normalized_index


# Mock data store (replaced database integration)
mock_trails = []


@app.get("/trails")
async def get_trails():
    """Get all trails from mock storage"""
    try:
        return {"success": True, "trails": mock_trails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/map")
async def get_map():
    """Generate map with all trails"""
    try:
        # If no trails, return empty map
        if not mock_trails:
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
        m = folium.Map(location=[-27.4698, 152.9560], zoom_start=12)

        # Color palette for different trails
        colors = ["blue", "red", "green", "purple", "orange", "darkred", "lightred"]

        for i, trail in enumerate(mock_trails):
            color = colors[i % len(colors)]
            coordinates = trail.get("coordinates", [])

            if coordinates:
                # Add polyline for this trail
                folium.PolyLine(
                    coordinates,
                    color=color,
                    weight=8,  # Increased thickness for easier clicking
                    opacity=0.9,  # Increased opacity
                    popup=f"<b>{trail.get('name', 'Unnamed Trail')}</b><br>Distance: {trail.get('distance', 0):.1f}km<br>Elevation Gain: {trail.get('elevation_gain', 0):.0f}m<br>Click for details",
                    tooltip=f"{trail.get('name', 'Unnamed Trail')} - Click for details",
                ).add_to(m)

                # Add start marker
                if coordinates:
                    start_coords = coordinates[0]
                    folium.Marker(
                        start_coords,
                        popup=f"Start: {trail.get('name', 'Unnamed Trail')}",
                        icon=folium.Icon(color="green", icon="play"),
                        tooltip=f"Start of {trail.get('name', 'Unnamed Trail')}",
                    ).add_to(m)

        # Add JavaScript for handling trail clicks
        js_code = f"""
        <script>
        // Store all trail data
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
        } for trail in mock_trails])};
        
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
            console.log('Setting up click handlers for', allTrailsData.length, 'trails');
            
            // Wait for Leaflet map to be ready
            if (typeof window.map === 'undefined') {{
                console.log('Map not ready yet, retrying...');
                setTimeout(setupClickHandlers, 500);
                return;
            }}
            
            // Method 1: Try to find and attach to path elements with better timing
            setTimeout(function() {{
                var paths = document.querySelectorAll('path.leaflet-interactive');
                console.log('Found', paths.length, 'interactive paths');
                
                // Also try other selectors
                if (paths.length === 0) {{
                    paths = document.querySelectorAll('path[stroke]');
                    console.log('Found', paths.length, 'stroke paths as fallback');
                }}
                
                paths.forEach(function(path, index) {{
                    if (index < allTrailsData.length) {{
                        path.addEventListener('click', function(e) {{
                            console.log('Trail path clicked:', index, allTrailsData[index]);
                            sendTrailDataToParent(allTrailsData[index]);
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }});
                        path.style.cursor = 'pointer';
                        path.style.strokeWidth = '8';
                        path.style.stroke = path.style.stroke || 'red'; // Ensure visibility
                        console.log('Added click handler to path', index, 'color:', path.style.stroke);
                    }}
                }});
            }}, 2000); // Wait even longer for paths to be ready
            
            // Method 2: Map click handler with distance-based trail selection
            if (window.map) {{
                window.map.on('click', function(e) {{
                    console.log('Map clicked at:', e.latlng);
                    
                    // Find closest trail to click point
                    var clickedLat = e.latlng.lat;
                    var clickedLng = e.latlng.lng;
                    var closestTrail = null;
                    var minDistance = Infinity;
                    
                    allTrailsData.forEach(function(trail) {{
                        if (trail.coordinates && trail.coordinates.length > 0) {{
                            trail.coordinates.forEach(function(coord) {{
                                var distance = Math.sqrt(
                                    Math.pow(coord[0] - clickedLat, 2) + 
                                    Math.pow(coord[1] - clickedLng, 2)
                                );
                                if (distance < minDistance) {{
                                    minDistance = distance;
                                    closestTrail = trail;
                                }}
                            }});
                        }}
                    }});
                    
                    // If clicked reasonably close to a trail
                    if (closestTrail && minDistance < 0.002) {{
                        console.log('Sending closest trail data:', closestTrail);
                        sendTrailDataToParent(closestTrail);
                    }} else {{
                        console.log('Click too far from trails, no trail selected');
                    }}
                }});
            }}
        }}
        
        // Start trying to set up click handlers
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, starting click handler setup');
            setTimeout(setupClickHandlers, 1000);
        }});
        
        // Fallback - try again after longer delay
        setTimeout(setupClickHandlers, 3000);
        </script>
        """

        m.get_root().html.add_child(folium.Element(js_code))

        # Generate unique filename
        map_id = str(uuid.uuid4())
        map_filename = f"trails_map_{map_id}.html"
        map_path = os.path.join(tempfile.gettempdir(), map_filename)

        # Save map to temporary file
        m.save(map_path)

        return {
            "success": True,
            "map_url": f"/maps/{map_filename}",
            "trails_count": len(mock_trails),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-gpx")
async def upload_gpx(file: UploadFile = File(...)):
    """Handle GPX file upload and save to mock storage"""
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

        # Simple difficulty calculation
        distance_factor = min(total_distance / 10, 1) * 3
        elevation_factor = min(elevation_gain / 1000, 1) * 4
        rolling_factor = 0.5 * 3  # simplified rolling hills
        difficulty_score = distance_factor + elevation_factor + rolling_factor

        if difficulty_score <= 3:
            difficulty_level = "Easy"
        elif difficulty_score <= 6:
            difficulty_level = "Moderate"
        elif difficulty_score <= 8:
            difficulty_level = "Hard"
        else:
            difficulty_level = "Extreme"

        # Create new trail
        new_trail = {
            "id": len(mock_trails) + 1,
            "name": trail_name,
            "distance": round(total_distance, 2),
            "elevation_gain": round(elevation_gain, 0),
            "elevation_loss": round(elevation_loss, 0),
            "max_elevation": round(max_elevation, 0),
            "min_elevation": round(min_elevation, 0),
            "rolling_hills_index": 0.5,  # simplified
            "difficulty_score": round(difficulty_score, 1),
            "difficulty_level": difficulty_level,
            "coordinates": coords,
            "elevation_profile": [
                {"distance": round(dist, 2), "elevation": round(ele, 1)}
                for dist, ele in zip(distances, elevations)
            ],
            "created_at": "2024-01-01T00:00:00Z",
        }

        mock_trails.append(new_trail)

        return {
            "success": True,
            "message": "Trail uploaded successfully",
            "trail": new_trail,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/maps/{filename}")
async def serve_map(filename: str):
    """Serve generated map files"""
    map_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(map_path):
        raise HTTPException(status_code=404, detail="Map file not found")
    return FileResponse(map_path)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
