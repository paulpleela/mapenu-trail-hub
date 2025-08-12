import gpxpy
from geopy.distance import geodesic
import matplotlib.pyplot as plt

def load_gpx_with_elevation(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude, point.elevation))
    return points

def cumulative_distances(points):
    distances = [0.0]
    for i in range(1, len(points)):
        prev = (points[i-1][0], points[i-1][1])
        curr = (points[i][0], points[i][1])
        dist = geodesic(prev, curr).km
        distances.append(distances[-1] + dist)
    return distances

def plot_elevation_profile(gpx_file):
    points = load_gpx_with_elevation(gpx_file)
    distances = cumulative_distances(points)
    elevations = [p[2] for p in points]

    plt.figure(figsize=(10, 5))
    plt.plot(distances, elevations, color='green')
    plt.xlabel('Distance (km)')
    plt.ylabel('Elevation (m)')
    plt.title('Elevation Profile of Mt Coot-tha Track')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Usage
gpx_path = "43-mt-coot-tha-summit-track.gpx"
plot_elevation_profile(gpx_path)
