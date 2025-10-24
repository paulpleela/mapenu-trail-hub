"""
Map generation routes
Handles interactive Folium map generation and serving
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from database import supabase
import folium
import os
import tempfile
import uuid
import json

router = APIRouter()


@router.get("/map")
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
            tiles="OpenStreetMap",  # Better base layer
            control_scale=True,  # Add scale control
            prefer_canvas=False,  # Ensure interactive behavior
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
                        max_width=250,
                    ),
                ).add_to(m)

                # Add start marker with better styling
                start_coord = coordinates[0]
                folium.Marker(
                    start_coord,
                    popup=folium.Popup(
                        f"<strong>Start:</strong> {trail.get('name', 'Unnamed Trail')}",
                        max_width=200,
                    ),
                    tooltip="Trail Start",
                    icon=folium.Icon(color="green", icon="play", prefix="fa"),
                ).add_to(m)

                # Add end marker with better styling
                end_coord = coordinates[-1]
                folium.Marker(
                    end_coord,
                    popup=folium.Popup(
                        f"<strong>End:</strong> {trail.get('name', 'Unnamed Trail')}",
                        max_width=200,
                    ),
                    tooltip="Trail End",
                    icon=folium.Icon(color="red", icon="stop", prefix="fa"),
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
                [max(lats) + lat_padding, max(lons) + lon_padding],
            ]

            m.fit_bounds(bounds)

        folium.TileLayer("OpenStreetMap").add_to(m)

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


@router.get("/maps/{filename}")
async def serve_map_file(filename: str):
    """Serve generated map files"""
    map_path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(map_path):
        raise HTTPException(status_code=404, detail="Map file not found")
    return FileResponse(map_path)
