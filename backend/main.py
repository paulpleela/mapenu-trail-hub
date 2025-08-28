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


def create_folium_map_from_gpx(gpx_content):
    """Create a Folium map from GPX content"""
    gpx = gpxpy.parse(gpx_content)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude, point.elevation or 0))

    if not coords:
        raise ValueError("No track points found in GPX file.")

    # Calculate cumulative distance (in km)
    distances = [0]
    for i in range(1, len(coords)):
        lat1, lon1, _ = coords[i - 1]
        lat2, lon2, _ = coords[i]
        distances.append(distances[-1] + haversine(lat1, lon1, lat2, lon2) / 1000)

    elevations = [ele for _, _, ele in coords]

    # Calculate rolling hills analysis
    rolling_hills_index = analyze_rolling_hills(elevations, distances)

    # Calculate trail statistics
    total_distance = distances[-1]
    elevation_gain = sum(
        max(0, elevations[i] - elevations[i - 1]) for i in range(1, len(elevations))
    )
    elevation_loss = sum(
        max(0, elevations[i - 1] - elevations[i]) for i in range(1, len(elevations))
    )
    max_elevation = max(elevations)
    min_elevation = min(elevations)

    # Plot elevation profile with rolling hills analysis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    # Elevation profile
    ax1.plot(distances, elevations, color="green", linewidth=2)
    ax1.set_xlabel("Distance (km)")
    ax1.set_ylabel("Elevation (m)")
    ax1.set_title("Elevation Profile")
    ax1.grid(True, alpha=0.3)
    ax1.fill_between(distances, elevations, alpha=0.3, color="green")

    # Rolling hills analysis
    elevation_changes = [0] + [
        abs(elevations[i] - elevations[i - 1]) for i in range(1, len(elevations))
    ]
    ax2.bar(distances, elevation_changes, width=0.01, color="orange", alpha=0.7)
    ax2.set_xlabel("Distance (km)")
    ax2.set_ylabel("Elevation Change (m)")
    ax2.set_title(f"Rolling Hills Analysis (Index: {rolling_hills_index:.2f})")
    ax2.grid(True, alpha=0.3)

    # Save plot to PNG in memory
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close(fig)

    # Create map
    avg_lat = sum(lat for lat, lon, ele in coords) / len(coords)
    avg_lon = sum(lon for lat, lon, ele in coords) / len(coords)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)

    # Create JavaScript function to communicate with parent window
    trail_data_js = f"""
    var trailData = {{
        distance: {total_distance:.2f},
        elevationGain: {elevation_gain:.0f},
        elevationLoss: {elevation_loss:.0f},
        maxElevation: {max_elevation:.0f},
        minElevation: {min_elevation:.0f},
        rollingHillsIndex: {rolling_hills_index:.2f},
        elevationProfile: {[{"distance": dist, "elevation": ele} for dist, (_, _, ele) in zip(distances, coords)]},
        chartImage: "data:image/png;base64,{encoded}"
    }};
    
    function sendTrailDataToParent() {{
        if (window.parent && window.parent !== window) {{
            window.parent.postMessage({{
                type: 'trail-clicked',
                data: trailData
            }}, '*');
        }}
    }}
    """

    # Add polyline with click event instead of popup
    folium.PolyLine(
        [(lat, lon) for lat, lon, ele in coords],
        color="blue",
        weight=4,
        opacity=0.8,
    ).add_to(m)

    # Add JavaScript to the map
    m.get_root().html.add_child(
        folium.Element(
            f"""
    <script>
    {trail_data_js}
    
    // Add click event to the polyline after map loads
    document.addEventListener('DOMContentLoaded', function() {{
        // Wait for Leaflet to be ready
        setTimeout(function() {{
            // Find all polylines and add click event
            var polylines = document.querySelectorAll('.leaflet-interactive');
            polylines.forEach(function(polyline) {{
                polyline.addEventListener('click', sendTrailDataToParent);
                polyline.style.cursor = 'pointer';
            }});
        }}, 1000);
    }});
    </script>
    """
        )
    )

    # Add start and end markers
    if coords:
        start_lat, start_lon, start_ele = coords[0]
        end_lat, end_lon, end_ele = coords[-1]

        folium.Marker(
            [start_lat, start_lon],
            popup=f"Start: {start_ele:.0f}m",
            icon=folium.Icon(color="green", icon="play"),
        ).add_to(m)

        folium.Marker(
            [end_lat, end_lon],
            popup=f"Finish: {end_ele:.0f}m",
            icon=folium.Icon(color="red", icon="stop"),
        ).add_to(m)

    return m, {
        "distance": total_distance,
        "elevation_gain": elevation_gain,
        "elevation_loss": elevation_loss,
        "max_elevation": max_elevation,
        "min_elevation": min_elevation,
        "rolling_hills_index": rolling_hills_index,
        "coords": coords,
    }


@app.post("/upload-gpx")
async def upload_gpx(file: UploadFile = File(...)):
    """Handle GPX file upload and return map HTML"""
    if not file.filename.lower().endswith(".gpx"):
        raise HTTPException(status_code=400, detail="File must be a GPX file")

    try:
        # Read GPX content
        content = await file.read()
        gpx_content = content.decode("utf-8")

        # Create Folium map
        folium_map, trail_stats = create_folium_map_from_gpx(gpx_content)

        # Generate unique filename
        map_id = str(uuid.uuid4())
        map_filename = f"trail_map_{map_id}.html"
        map_path = os.path.join(tempfile.gettempdir(), map_filename)

        # Save map to temporary file
        folium_map.save(map_path)

        return {
            "success": True,
            "map_url": f"/maps/{map_filename}",
            "trail_stats": trail_stats,
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


@app.get("/demo-map")
async def demo_map():
    """Create a demo map for testing"""
    try:
        # Use the existing GPX file if available
        gpx_path = "./data/43-mt-coot-tha-summit-track.gpx"

        if os.path.exists(gpx_path):
            with open(gpx_path, "r") as f:
                gpx_content = f.read()

            folium_map, trail_stats = create_folium_map_from_gpx(gpx_content)

            # Generate unique filename
            map_id = str(uuid.uuid4())
            map_filename = f"demo_map_{map_id}.html"
            map_path = os.path.join(tempfile.gettempdir(), map_filename)

            # Save map
            folium_map.save(map_path)

            response_data = {
                "success": True,
                "map_url": f"/maps/{map_filename}",
                "trail_stats": trail_stats,
            }
            print(f"Returning response: {response_data}")
            return response_data
        else:
            error_msg = f"Demo GPX file not found at {os.path.abspath(gpx_path)}"
            print(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)

    except Exception as e:
        error_msg = f"Error creating demo map: {str(e)}"
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
