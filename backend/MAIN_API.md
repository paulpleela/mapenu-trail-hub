# MAPENU Backend API Reference

This document lists the main FastAPI endpoints implemented in `backend/main.py`, their purpose, inputs, outputs, and example usage.

## Authentication / Environment

- The backend expects Supabase environment variables in `.env`: `SUPABASE_URL` and `SUPABASE_KEY`.
- Without these, the app will not start.

## Endpoints

### GET /trails

Description: Returns all trails stored in Supabase.

Response (200):

```json
{ "success": true, "trails": [ ... ] }
```

Errors:

- 500 if database query fails.

Example:
curl http://127.0.0.1:8000/trails

---

### GET /trail/{trail_id}/similar

Description: Return a list of trails similar to the specified trail.

Params:

- `trail_id` (int) — Trail database id
- `limit` (query, optional) — Number of similar trails to return (default 5)

Response (200):

```json
{ "success": true, "target_trail": "Trail Name", "similar_trails": [ {"trail": {...}, "similarity_score": 0.82 } ] }
```

Errors:

- 404 if trail not found
- 500 on server error

---

### GET /analytics/overview

Description: Returns aggregated analytics for all trails (counts, distributions, top items).

Response (200):

```json
{ "success": true, "analytics": { "total_trails": 12, ... } }
```

---

### GET /trail/{trail_id}/weather

Description: Returns simulated live weather difficulty adjustment and exposure info for a trail.

Response (200):

```json
{
  "success": true,
  "trail_name": "Example Trail",
  "live_weather": { "multiplier": 1.2, "conditions": "5°C, 25km/h winds" },
  "weather_exposure": { "exposure_level": "Moderate", ... },
  "updated_difficulty": { "base_difficulty": 4.0, "weather_adjusted": 4.8 }
}
```

Notes: This uses a simulated weather generator for demo purposes. Replace with a real weather API for production.

---

### GET /map

Description: Generates an interactive Folium map showing all trails and returns a URL to a temporary HTML file.

Response (200):

```json
{
  "success": true,
  "map_url": "/maps/trails_map_<uuid>.html",
  "trails_count": 3
}
```

Client usage:

1. Call `/map` and retrieve `map_url`.
2. Fetch `http://127.0.0.1:8000{map_url}` in browser to view the map (the server serves the file via `/maps/{filename}`).

Common issues:

- 500 errors usually indicate a database problem or a failure generating the map (check server logs).

---

### POST /upload-gpx

Description: Upload a GPX file to add a trail to Supabase and run local analysis for elevation, difficulty, and segments.

Form Data:

- `file` — GPX file (multipart/form-data)

Response (200):

```json
{ "success": true, "message": "Trail uploaded successfully to database", "trail": { ... } }
```

Errors:

- 400 for invalid file format or no track points
- 409 for duplicate trail (by name or nearby start point)
- 500 on DB insertion error

Notes on GPX processing:

- The endpoint extracts coordinates, elevation, computes distances using haversine, slope, rolling hills index, segments, and a difficulty_score. It stores the trail with enriched analytics fields in Supabase.

---

### GET /trail/{trail_id}/elevation-sources

Description: Returns elevation profiles from multiple data sources for comparison and validation. This endpoint extracts elevation data from GPX, LiDAR point clouds, and QSpatial DEM tiles, then provides an averaged "Overall" profile.

Params:

- `trail_id` (int) — Trail database id

Response (200):

```json
{
  "success": true,
  "trail_id": 5,
  "trail_name": "Mt Coot-tha Summit Track",
  "sources": {
    "Overall": {
      "available": true,
      "elevations": [45.2, 47.8, 50.1, ...],
      "distances": [0, 0.05, 0.10, ...],
      "slopes": [0, 5.2, 4.6, ...],
      "coordinates": [[lat, lon], ...],
      "source": "Average of 3 sources: GPX, LiDAR, QSpatial",
      "data_points": 234,
      "sources_used": 3,
      "source_names": ["GPX", "LiDAR", "QSpatial"]
    },
    "GPX": {
      "available": true,
      "elevations": [...],
      "distances": [...],
      "slopes": [...],
      "source": "Original GPX file",
      "data_points": 234
    },
    "LiDAR": {
      "available": true,
      "elevations": [...],
      "distances": [...],
      "slopes": [...],
      "source": "LiDAR point cloud: trail_1.las",
      "coverage_percent": 98.5,
      "total_lidar_points": 2450000,
      "data_points": 230
    },
    "QSpatial": {
      "available": true,
      "elevations": [...],
      "distances": [...],
      "slopes": [...],
      "source": "QSpatial 1m DEM tiles",
      "resolution": "1 meter",
      "tiles_used": 4,
      "data_points": 234
    }
  },
  "summary": {
    "total_sources_available": 4,
    "gpx_available": true,
    "lidar_available": true,
    "qspatial_available": true,
    "overall_available": true
  }
}
```

Errors:

- 404 if trail not found
- 500 if extraction fails for all sources

Notes:

- Each source includes `elevations`, `distances` (km), `slopes` (%), and metadata
- `available: false` indicates source not accessible (missing data files or coverage)
- LiDAR extraction uses KD-Tree nearest-neighbor search within 2m radius
- DEM extraction uses existing `RealDEMAnalyzer` with windowed reading
- Overall profile averages all available sources at each point
- Coordinates automatically converted to GDA94 MGA Zone 56 for alignment

Example:

```bash
curl http://127.0.0.1:8000/trail/5/elevation-sources
```

---

### GET /maps/{filename}

Description: Serves temporary HTML files previously generated (map pages saved in the OS temp directory by `/map`).

Response:

- Returns the HTML file contents as `text/html`.

Errors:

- 404 if the file does not exist in the temp directory

---

## Implementation notes

- Map files are saved to the OS temporary directory with a UUID filename and served through `/maps/{filename}`. If you see `404` for map files, check that the server process still has the temporary file (temp files may be cleaned up by OS or other processes).
- The backend relies on Supabase table `trails` with expected fields such as `id`, `name`, `coordinates`, `distance`, `elevation_gain`, `elevation_profile`, etc.
- Error handling currently logs exceptions and returns 500-level errors; more fine-grained error messages could be added.

## Examples

Upload GPX with curl:

```bash
curl -F "file=@/path/to/your/track.gpx" http://127.0.0.1:8000/upload-gpx
```

Get the map and open in browser (PowerShell example):

```powershell
$resp = Invoke-RestMethod http://127.0.0.1:8000/map
Start-Process "http://127.0.0.1:8000$($resp.map_url)"
```

## Troubleshooting

- If `/map` returns 500, check server console for the exception trace. Common problems:
  - Missing Supabase credentials in `.env`
  - Empty `trails` table leading to unexpected behavior (the endpoint handles empty but verify DB access)
  - Folium tile attribution network errors if offline
- If map HTML returns 404 when fetching `/maps/{filename}`, verify the file still exists in the OS temp dir. The server must be the same process that created the file.
