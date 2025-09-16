# DEM Analysis (MAPENU)

This document describes the DEM analysis features in the MAPENU backend, how to use them, and troubleshooting tips.

## Files
- `real_dem_analysis.py` — Core DEM analysis module.
  - Responsibilities: locate relevant DEM tiles, extract elevation profiles for GPX/trail coordinates, analyze terrain features, and produce 3D visualizations (interactive Plotly HTML or static images).
- `main.py` — FastAPI application exposing endpoints that utilize `real_dem_analysis.py`.

## Features
- Extract accurate elevation profiles from local GeoTIFF DEM tiles.
- Generate terrain feature analysis (slope, aspect, rolling hills index, terrain variety).
- Produce focused 3D visualizations cropped to the exact bounds of a trail.
- Support for LiDAR workflows exists in `lidar_trail_analysis.py` (separate documentation).

## Key API endpoints (in `main.py`)
- `GET /map` — Generates an interactive Folium map of all trails and returns a URL to a temporary HTML file.
- `GET /trail/{trail_id}/dem-analysis` — Run DEM analysis for a given trail:
  - Returns elevation profile, terrain features, and a 3D visualization payload.
- `GET /trail/{trail_id}/dem-overlay-map` — Generates a Folium map colored by elevation along the trail (returns URL to temporary HTML file).
- `GET /trail/{trail_id}/3d-terrain` — Returns a JSON wrapper that may contain `visualization_html` (interactive Plotly) or a static image.
- `GET /trail/{trail_id}/3d-terrain-viewer` — Returns a standalone HTML page containing the Plotly interactive visualization.
- `GET /dem/coverage` — Returns metadata about available DEM tiles and coverage.

## How it works (high-level)
1. Convert trail coordinates (lat, lon) to the DEM coordinate system (GDA94/MGA Zone 56 or dataset CRS) using `pyproj` in `real_dem_analysis._coords_to_gda94()`.
2. Locate DEM tiles that intersect the trail using `_find_relevant_dem_tiles()` (by bounding box or spatial indexing).
3. For visualization, compute the minimal bounding window from the trail min/max coordinates and read only that window via `rasterio.windows.Window` for performance.
4. Map trail points to raster pixel coordinates, extract elevation values, and build an elevation profile.
5. Create an interactive Plotly surface (if Plotly is available) and overlay the trail as a 3D scatter/line; fallback to a static Matplotlib plot if needed.

## Usage examples

From your terminal (after starting the backend):

1) Get DEM coverage info:

   curl http://127.0.0.1:8000/dem/coverage

2) Run DEM analysis for trail with id 5:

   curl http://127.0.0.1:8000/trail/5/dem-analysis

3) Open the 3D viewer for trail id 5 in browser:

   http://127.0.0.1:8000/trail/5/3d-terrain-viewer


## Endpoint response shapes
- `GET /trail/{id}/dem-analysis` returns JSON like:

```json
{
  "success": true,
  "trail_name": "Example Trail",
  "elevation_analysis": {
     "elevation_profile": { "distances": [...], "elevations": [...], "coordinates": [...] },
     "statistics": { "min_elevation": ..., "max_elevation": ..., "elevation_gain": ... }
  },
  "terrain_features": { /* slope, aspect, variety, rolling hills */ },
  "visualization_3d": { "type": "interactive", "html_content": "<html>...</html>" }
}
```

## Troubleshooting

- Plotly errors with colorscales: Plotly expects specific names for `colorscale`. If you see errors like "Invalid value for colorscale: 'terrain'", change to a valid colorscale like `'earth'` or `'viridis'`.
- Trail not visible / floating: ensure coordinate reprojection is correct. Check that `_coords_to_gda94()` is returning values in the same CRS as the dataset. Look for printed debug logs showing point mapping.
- No tiles found: confirm `dem_path` points to the correct DEM folder. Use absolute path resolved with `os.path.join(os.path.dirname(__file__), 'data', ...)`.
- Large data slowdown: the module reads only windowed subsets; increase buffer only if you need surrounding context.

## Performance Tips
- Keep the DEM directory local (SSD) for best read performance.
- If multiple tiles are needed, consider building a lightweight spatial index (GeoJSON of tile bounds) to speed up tile lookup.
- Downsample the DEM for interactive previews (reduce resolution for Plotly surface generation).

## Testing
- Use the included `test_installation.py` (created by the setup script) or manually run small queries against `/trail/{id}/dem-analysis` using a trail you know has coordinates inside the DEM tiles.
