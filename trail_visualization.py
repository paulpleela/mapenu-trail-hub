import gpxpy
import folium

def plot_gpx_on_map(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)

    # Extract track points
    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude))

    # Center map around the average lat/lon of the trail
    avg_lat = sum(lat for lat, lon in coords) / len(coords)
    avg_lon = sum(lon for lat, lon in coords) / len(coords)

    # Create map centered on trail
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)

    # Add trail polyline
    folium.PolyLine(coords, color='blue', weight=4, opacity=0.7).add_to(m)

    return m

# Usage
gpx_path = "43-mt-coot-tha-summit-track.gpx"
map_object = plot_gpx_on_map(gpx_path)
map_object.save("mt_coot_tha_trail_map.html")
