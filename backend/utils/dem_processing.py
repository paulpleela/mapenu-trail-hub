"""
DEM (Digital Elevation Model) processing utilities.
"""
import os
import glob
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
from scipy.interpolate import griddata


def find_relevant_dem_tiles(trail_coords):
    """
    Find DEM tiles that cover the trail coordinates.
    
    Args:
        trail_coords: List of [lat, lon] coordinates
    
    Returns:
        list: Paths to relevant DEM .tif files
    """
    if not trail_coords:
        return []

    dem_dir = os.path.join("data", "QSpatial", "DEM", "1 Metre")

    if not os.path.exists(dem_dir):
        print(f"DEM directory not found: {dem_dir}")
        return []

    # Get all available DEM files
    dem_files = glob.glob(os.path.join(dem_dir, "*.tif"))

    # For simplified version, return first 4 tiles
    # In production, filter by bounds
    return dem_files[:4]


def process_dem_for_trail(trail_coords, dem_files, resolution_factor=4):
    """
    Process DEM data for 3D visualization of a trail.
    
    Args:
        trail_coords: List of [lat, lon] trail coordinates
        dem_files: List of DEM file paths
        resolution_factor: Downsampling factor (higher = faster but lower quality)
    
    Returns:
        dict: Processed terrain data with surface and trail_line, or None
    """
    if not dem_files or not trail_coords:
        return None

    try:
        print(
            f"Processing DEM with {len(dem_files)} files and {len(trail_coords)} trail coordinates"
        )

        # Calculate bounding box for the trail
        lats = [coord[0] for coord in trail_coords]
        lons = [coord[1] for coord in trail_coords]

        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        print(
            f"Trail bounds: lat {min_lat:.6f} to {max_lat:.6f}, lon {min_lon:.6f} to {max_lon:.6f}"
        )

        # Try to process real DEM data
        try:
            with rasterio.open(dem_files[0]) as dem:
                print(f"DEM CRS: {dem.crs}")
                print(f"DEM bounds: {dem.bounds}")
                print(f"DEM shape: {dem.shape}")

                elevation_data = dem.read(1)
                transform_matrix = dem.transform

                # Get subset for performance
                height, width = elevation_data.shape
                step = resolution_factor * 10

                subset_height = height // step
                subset_width = width // step

                if subset_height < 10 or subset_width < 10:
                    raise ValueError("DEM subset too small")

                # Extract elevation points
                x_coords = []
                y_coords = []
                elevations = []

                for i in range(0, subset_height):
                    for j in range(0, subset_width):
                        row = i * step
                        col = j * step
                        if row < height and col < width:
                            elevation = float(elevation_data[row, col])
                            if not np.isnan(elevation) and elevation > -9999:
                                x, y = rasterio.transform.xy(transform_matrix, row, col)
                                lon, lat = transform(
                                    dem.crs, CRS.from_epsg(4326), [x], [y]
                                )
                                x_coords.append(lon[0])
                                y_coords.append(lat[0])
                                elevations.append(elevation)

                print(f"Extracted {len(elevations)} elevation points from DEM")

                if len(elevations) >= 100:
                    # Create regular grid for 3D surface
                    grid_size = 30
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)

                    xi = np.linspace(x_min, x_max, grid_size)
                    yi = np.linspace(y_min, y_max, grid_size)
                    xi_grid, yi_grid = np.meshgrid(xi, yi)

                    # Interpolate elevations onto regular grid
                    points = np.column_stack((x_coords, y_coords))
                    zi_grid = griddata(
                        points, elevations, (xi_grid, yi_grid), method="linear"
                    )

                    # Fill NaN values
                    mask = np.isnan(zi_grid)
                    if np.any(mask):
                        zi_grid_filled = griddata(
                            points, elevations, (xi_grid, yi_grid), method="nearest"
                        )
                        zi_grid[mask] = zi_grid_filled[mask]

                    # Process trail line
                    trail_line = []
                    for coord in trail_coords[::5]:
                        lat, lon = coord
                        if x_min <= lon <= x_max and y_min <= lat <= y_max:
                            trail_elev = griddata(
                                points, elevations, (lon, lat), method="linear"
                            )
                            if np.isnan(trail_elev):
                                trail_elev = griddata(
                                    points, elevations, (lon, lat), method="nearest"
                                )

                            if not np.isnan(trail_elev):
                                trail_line.append(
                                    {"x": lon, "y": lat, "z": float(trail_elev)}
                                )

                    surface_data = {
                        "x": xi.tolist(),
                        "y": yi.tolist(),
                        "z": zi_grid.tolist(),
                        "bounds": {
                            "x_min": float(x_min),
                            "x_max": float(x_max),
                            "y_min": float(y_min),
                            "y_max": float(y_max),
                            "z_min": float(np.nanmin(zi_grid)),
                            "z_max": float(np.nanmax(zi_grid)),
                        },
                    }

                    return {
                        "surface": surface_data,
                        "trail_line": trail_line,
                        "metadata": {
                            "grid_size": grid_size,
                            "num_trail_points": len(trail_line),
                            "elevation_range": float(
                                np.nanmax(zi_grid) - np.nanmin(zi_grid)
                            ),
                            "data_source": "Brisbane DEM",
                        },
                    }

        except Exception as dem_error:
            print(f"DEM processing failed: {dem_error}")
            return None

    except Exception as e:
        print(f"Error processing DEM: {e}")
        return None
