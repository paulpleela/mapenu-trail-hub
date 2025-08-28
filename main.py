import gpxpy
import folium
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import math

# REF: ChatGPT was used to help write this function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def plot_gpx_with_elevation_popup(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)

    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.latitude, point.longitude, point.elevation))

    if not coords:
        raise ValueError("No track points found in GPX file.")

    # Calculate cumulative distance (in km)
    distances = [0]
    for i in range(1, len(coords)):
        lat1, lon1, _ = coords[i-1]
        lat2, lon2, _ = coords[i]
        distances.append(distances[-1] + haversine(lat1, lon1, lat2, lon2) / 1000)

    elevations = [ele for _, _, ele in coords]

    # Plot elevation profile
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(distances, elevations, color='green')
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Elevation (m)")
    ax.set_title("Elevation Profile")
    ax.grid(True)

    # Save plot to PNG in memory
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    # Create map
    avg_lat = sum(lat for lat, lon, ele in coords) / len(coords)
    avg_lon = sum(lon for lat, lon, ele in coords) / len(coords)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14)

    # Add polyline with popup chart
    html = f'<img src="data:image/png;base64,{encoded}" width="600">'
    iframe = folium.IFrame(html, width=650, height=350)
    popup = folium.Popup(iframe, max_width=650)
    folium.PolyLine(
        [(lat, lon) for lat, lon, ele in coords],
        color='blue',
        weight=4,
        opacity=0.7,
        popup=popup
    ).add_to(m)

    return m

# SOURCE FOR THE GPX DATA: # https://www.aussiebushwalking.com/qld/se-qld/brisbane-forest-park-d-aguilar-np/mt-coot-tha/mt-coot-tha-summit-track#:~:text=GPS%20Tracks
gpx_path = "43-mt-coot-tha-summit-track.gpx"
map_object = plot_gpx_with_elevation_popup(gpx_path)
map_object.save("mt_coot_tha_trail_with_profile.html")
