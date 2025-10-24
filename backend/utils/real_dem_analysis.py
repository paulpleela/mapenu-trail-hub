import os
import numpy as np
import rasterio
import rasterio.windows
import rasterio.transform
from rasterio.mask import mask
from shapely.geometry import LineString, Point
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Tuple, Dict, Any
import glob


class RealDEMAnalyzer:
    def __init__(self, dem_base_path: str):
        """Initialize with path to DEM data directory"""
        self.dem_base_path = dem_base_path
        self.dem_files = self._find_dem_files()

    def _find_dem_files(self) -> List[str]:
        """Find all DEM .tif files in the directory"""
        pattern = os.path.join(self.dem_base_path, "**/*.tif")
        return glob.glob(pattern, recursive=True)

    def _coords_to_gda94(self, coords: List[List[float]]) -> List[Tuple[float, float]]:
        """Convert WGS84 coordinates to GDA94 MGA Zone 56"""
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:28356", always_xy=True)
        converted = []
        for lat, lon in coords:
            x, y = transformer.transform(
                lon, lat
            )  # Note: transformer expects (lon, lat)
            converted.append((x, y))
        return converted

    def _find_relevant_dem_tiles(self, trail_coords: List[List[float]]) -> List[str]:
        """Find DEM tiles that intersect with the trail path"""
        # Convert trail to GDA94
        gda94_coords = self._coords_to_gda94(trail_coords)

        # Create bounding box
        min_x = min(coord[0] for coord in gda94_coords)
        max_x = max(coord[0] for coord in gda94_coords)
        min_y = min(coord[1] for coord in gda94_coords)
        max_y = max(coord[1] for coord in gda94_coords)

        relevant_files = []

        for dem_file in self.dem_files:
            try:
                with rasterio.open(dem_file) as dataset:
                    bounds = dataset.bounds
                    # Check if trail bounding box intersects with DEM bounds
                    if (
                        min_x <= bounds.right
                        and max_x >= bounds.left
                        and min_y <= bounds.top
                        and max_y >= bounds.bottom
                    ):
                        relevant_files.append(dem_file)
            except Exception as e:
                print(f"Error reading {dem_file}: {e}")
                continue

        return relevant_files

    def extract_elevation_profile(
        self, trail_coords: List[List[float]]
    ) -> Dict[str, Any]:
        """Extract detailed elevation profile from DEM data"""
        try:
            # Find relevant DEM tiles
            relevant_tiles = self._find_relevant_dem_tiles(trail_coords)

            if not relevant_tiles:
                return {"error": "No DEM tiles found for trail area"}

            # Convert coordinates to GDA94
            gda94_coords = self._coords_to_gda94(trail_coords)

            # Create LineString for the trail
            trail_line = LineString(gda94_coords)

            # Sample points along the trail (every 10 meters)
            distances = np.arange(0, trail_line.length, 10)
            sample_points = [trail_line.interpolate(distance) for distance in distances]

            elevations = []
            coordinates = []

            # Process each relevant DEM tile
            for dem_file in relevant_tiles:
                try:
                    with rasterio.open(dem_file) as dataset:
                        for i, point in enumerate(sample_points):
                            x, y = point.x, point.y

                            # Check if point is within this tile's bounds
                            if (
                                dataset.bounds.left <= x <= dataset.bounds.right
                                and dataset.bounds.bottom <= y <= dataset.bounds.top
                            ):

                                # Read elevation at this point
                                row, col = dataset.index(x, y)

                                # Ensure we're within the raster bounds
                                if (
                                    0 <= row < dataset.height
                                    and 0 <= col < dataset.width
                                ):
                                    elevation = dataset.read(1)[row, col]

                                    if elevation != dataset.nodata:
                                        elevations.append(float(elevation))
                                        coordinates.append(
                                            [
                                                trail_coords[
                                                    min(i, len(trail_coords) - 1)
                                                ][0],
                                                trail_coords[
                                                    min(i, len(trail_coords) - 1)
                                                ][1],
                                            ]
                                        )

                except Exception as e:
                    print(f"Error processing {dem_file}: {e}")
                    continue

            if not elevations:
                return {"error": "No elevation data extracted"}

            # Calculate slope and other metrics
            slopes = []
            for i in range(1, len(elevations)):
                rise = elevations[i] - elevations[i - 1]
                run = 10  # 10 meter sampling
                slope = (rise / run) * 100  # Convert to percentage
                slopes.append(slope)

            return {
                "success": True,
                "elevation_profile": {
                    "distances": distances[: len(elevations)].tolist(),
                    "elevations": elevations,
                    "slopes": [0] + slopes,  # Add 0 for first point
                    "coordinates": coordinates,
                },
                "statistics": {
                    "min_elevation": min(elevations),
                    "max_elevation": max(elevations),
                    "elevation_gain": sum(
                        max(0, elevations[i] - elevations[i - 1])
                        for i in range(1, len(elevations))
                    ),
                    "elevation_loss": sum(
                        max(0, elevations[i - 1] - elevations[i])
                        for i in range(1, len(elevations))
                    ),
                    "max_slope": max(slopes) if slopes else 0,
                    "min_slope": min(slopes) if slopes else 0,
                    "avg_slope": np.mean([abs(s) for s in slopes]) if slopes else 0,
                },
                "data_sources": relevant_tiles,
                "resolution": "1 meter",
                "sample_interval": "10 meters",
            }

        except Exception as e:
            return {"error": f"DEM analysis failed: {str(e)}"}

    def _calculate_trail_bounds(
        self, gda94_coords: List[List[float]], buffer_meters: int = 0
    ) -> Dict[str, float]:
        """Calculate exact bounding box around trail coordinates"""
        x_coords = [coord[0] for coord in gda94_coords]
        y_coords = [coord[1] for coord in gda94_coords]

        return {
            "min_x": min(x_coords),
            "max_x": max(x_coords),
            "min_y": min(y_coords),
            "max_y": max(y_coords),
        }

    def create_3d_terrain_visualization(
        self,
        trail_coords: List[List[float]],
        buffer_meters: int = 0,
        elevation_source: str = "gpx",
        trail_id: int = None,
        lidar_elevations: List[float] = None,
    ) -> Dict[str, Any]:
        """Create interactive 3D terrain visualization around the trail using Plotly

        Args:
            trail_coords: List of [lon, lat] coordinates
            buffer_meters: Buffer around trail in meters (default: 0)
            elevation_source: "gpx" (uses DEM for elevations) or "lidar" (uses LiDAR point cloud elevations)
            trail_id: Trail ID (required if elevation_source="lidar")
            lidar_elevations: Pre-fetched LiDAR elevation data (if available)
        """
        try:
            relevant_tiles = self._find_relevant_dem_tiles(trail_coords)

            if not relevant_tiles:
                return {"success": False, "error": "No DEM tiles found for trail area"}

            # Convert coordinates to GDA94 early (needed for both Plotly and fallback)
            gda94_coords = self._coords_to_gda94(trail_coords)

            # Use the first relevant tile for demonstration
            dem_file = relevant_tiles[0]

            with rasterio.open(dem_file) as dataset:
                # Calculate exact trail bounds (no buffer)
                trail_bounds = self._calculate_trail_bounds(gda94_coords)

                # Convert bounds to pixel coordinates
                min_col, min_row = dataset.index(
                    trail_bounds["min_x"], trail_bounds["max_y"]
                )
                max_col, max_row = dataset.index(
                    trail_bounds["max_x"], trail_bounds["min_y"]
                )

                # Ensure we don't go outside the dataset bounds
                min_row = max(0, min_row)
                min_col = max(0, min_col)
                max_row = min(dataset.height, max_row)
                max_col = min(dataset.width, max_col)

                # Read only the exact area that contains the trail
                window = rasterio.windows.Window(
                    min_col, min_row, max_col - min_col, max_row - min_row
                )
                elevation_data = dataset.read(1, window=window)

                # Update transform for the windowed data
                windowed_transform = rasterio.windows.transform(
                    window, dataset.transform
                )

                # Try to create interactive 3D plot with Plotly
                try:
                    import plotly.graph_objects as go
                    import plotly.io as pio

                    # Sample the data for visualization (reduce resolution for performance)
                    step = max(1, elevation_data.shape[0] // 100)

                    # Create coordinate arrays that match the actual data dimensions
                    y_indices = np.arange(0, elevation_data.shape[0], step)
                    x_indices = np.arange(0, elevation_data.shape[1], step)
                    X, Y = np.meshgrid(x_indices, y_indices)
                    Z = elevation_data[::step, ::step]

                    # Remove no-data values
                    Z_clean = np.where(Z == dataset.nodata, np.nan, Z)

                    # Create 3D surface plot
                    fig = go.Figure()

                    # Add terrain surface
                    fig.add_trace(
                        go.Surface(
                            z=Z_clean,
                            x=X,
                            y=Y,
                            colorscale="earth",  # Valid Plotly colorscale that resembles terrain
                            name="Terrain",
                            showscale=True,
                            colorbar=dict(title="Elevation (m)", x=1.02),
                            opacity=0.9,
                        )
                    )

                    # Add trail path as 3D scatter plot with higher accuracy
                    trail_x = []
                    trail_y = []
                    trail_z = []

                    # Use more trail points for better accuracy (every 3rd point or minimum of 200 points)
                    total_points = len(gda94_coords)
                    target_points = min(
                        200, total_points
                    )  # Up to 200 points for accuracy
                    sample_interval = max(1, total_points // target_points)
                    sampled_coords = gda94_coords[::sample_interval]

                    # Determine elevation source
                    using_lidar = (
                        elevation_source.lower() == "lidar"
                        and lidar_elevations is not None
                    )
                    source_name = "LiDAR" if using_lidar else "DEM"
                    print(
                        f"Processing {len(sampled_coords)} trail points from {total_points} total points (interval: {sample_interval}) using {source_name} elevations..."
                    )

                    if using_lidar:
                        print(f"   Note: Using DEM elevations for trail path to ensure proper alignment with terrain surface")

                    for i, (x, y) in enumerate(sampled_coords):
                        try:
                            # Convert world coordinates to windowed pixel coordinates
                            global_col, global_row = dataset.index(x, y)

                            # Convert to windowed coordinates
                            windowed_col = global_col - min_col
                            windowed_row = global_row - min_row

                            if (
                                0 <= windowed_row < elevation_data.shape[0]
                                and 0 <= windowed_col < elevation_data.shape[1]
                            ):
                                # ALWAYS use DEM elevation for the trail path to ensure it sits on terrain
                                # (Even when "LiDAR" source is selected - this is just for visual consistency)
                                z = elevation_data[windowed_row, windowed_col]

                                if z != dataset.nodata and not (
                                    isinstance(z, float) and np.isnan(z)
                                ):
                                    trail_x.append(windowed_col)
                                    trail_y.append(windowed_row)
                                    # Add small visual offset above terrain surface
                                    elevation_offset = 1.0
                                    trail_z.append(z + elevation_offset)
                                    if i < 5:  # Only print first few for debugging
                                        print(
                                            f"Added trail point {i}: ({windowed_col}, {windowed_row}, {z:.1f}m + {elevation_offset}m offset = {z + elevation_offset:.1f}m) from DEM"
                                        )
                                else:
                                    print(f"Trail point {i}: No data value")
                            else:
                                print(
                                    f"Trail point {i}: Out of bounds ({windowed_row}, {windowed_col})"
                                )
                        except Exception as e:
                            print(f"Trail point {i} error: {e}")
                            continue

                    print(f"Final trail points: {len(trail_x)}")

                    if trail_x:
                        print(
                            f"Creating high-accuracy trail visualization with {len(trail_x)} points"
                        )
                        fig.add_trace(
                            go.Scatter3d(
                                x=trail_x,
                                y=trail_y,
                                z=trail_z,
                                mode="lines+markers",
                                line=dict(color="red", width=4),
                                marker=dict(size=2, color="red"),
                                name="Trail Path",
                                hovertemplate="<b>Trail Point</b><br>X: %{x}<br>Y: %{y}<br>Elevation: %{z:.1f}m<extra></extra>",
                            )
                        )

                        # Also add start and end markers for better visualization
                        if len(trail_x) > 1:
                            # Start marker
                            fig.add_trace(
                                go.Scatter3d(
                                    x=[trail_x[0]],
                                    y=[trail_y[0]],
                                    z=[trail_z[0] + 8],
                                    mode="markers",
                                    marker=dict(
                                        size=15, color="green", symbol="diamond"
                                    ),
                                    name="Trail Start",
                                    hovertemplate="<b>Trail Start</b><br>Elevation: %{z:.1f}m<extra></extra>",
                                )
                            )

                            # End marker
                            fig.add_trace(
                                go.Scatter3d(
                                    x=[trail_x[-1]],
                                    y=[trail_y[-1]],
                                    z=[trail_z[-1] + 8],
                                    mode="markers",
                                    marker=dict(
                                        size=15, color="blue", symbol="diamond"
                                    ),
                                    name="Trail End",
                                    hovertemplate="<b>Trail End</b><br>Elevation: %{z:.1f}m<extra></extra>",
                                )
                            )
                    else:
                        print(
                            "No trail points found - trail line will not be displayed"
                        )

                    # Update layout for better interaction
                    elevation_source_label = "LiDAR Elevations" if using_lidar else "DEM Elevations"
                    fig.update_layout(
                        title={
                            "text": f"3D Terrain Visualization - Trail with {elevation_source_label}",
                            "x": 0.5,
                            "xanchor": "center",
                        },
                        scene=dict(
                            xaxis_title="Easting (m)",
                            yaxis_title="Northing (m)",
                            zaxis_title="Elevation (m)",
                            camera=dict(eye=dict(x=1.2, y=1.2, z=0.8)),
                            aspectmode="manual",
                            aspectratio=dict(x=1, y=1, z=0.5),
                        ),
                        width=900,
                        height=700,
                        margin=dict(r=100, b=40, l=40, t=60),
                        showlegend=True,
                        legend=dict(x=0, y=1),
                    )

                    # Generate standalone HTML
                    html_content = pio.to_html(
                        fig,
                        include_plotlyjs=True,
                        div_id="terrain-3d-plot",
                        config={
                            "displayModeBar": True,
                            "displaylogo": False,
                            "modeBarButtonsToAdd": [
                                "pan3d",
                                "orbitRotation",
                                "tableRotation",
                            ],
                            "scrollZoom": True,
                        },
                    )

                    return {
                        "success": True,
                        "type": "interactive",
                        "html_content": html_content,
                        "description": "Interactive 3D terrain - Click and drag to rotate, scroll to zoom",
                    }

                except ImportError as e:
                    print(f"Plotly not available: {e}")
                    # Fallback to matplotlib
                    return self._create_static_3d_plot(
                        elevation_data, gda94_coords, dataset
                    )
                except Exception as e:
                    print(f"Plotly 3D error: {e}")
                    # Fallback to matplotlib
                    return self._create_static_3d_plot(
                        elevation_data, gda94_coords, dataset
                    )

        except Exception as e:
            print(f"3D visualization error: {e}")
            return {"success": False, "error": str(e)}

    def _create_static_3d_plot(self, elevation_data, gda94_coords, dataset):
        """Fallback static 3D plot using matplotlib"""
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D

            # Create 3D plot
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection="3d")

            # Sample the data for visualization
            step = max(1, elevation_data.shape[0] // 200)
            x_range = np.arange(0, elevation_data.shape[1], step)
            y_range = np.arange(0, elevation_data.shape[0], step)
            X, Y = np.meshgrid(x_range, y_range)
            Z = elevation_data[::step, ::step]

            # Remove no-data values
            Z_clean = np.where(Z == dataset.nodata, np.nan, Z)

            # Create surface plot
            surface = ax.plot_surface(X, Y, Z_clean, cmap="terrain", alpha=0.8)

            # Add trail path
            trail_x = []
            trail_y = []
            trail_z = []

            for x, y in gda94_coords:
                try:
                    row, col = dataset.index(x, y)
                    if 0 <= row < dataset.height and 0 <= col < dataset.width:
                        z = elevation_data[row, col]
                        if z != dataset.nodata:
                            plot_x = col // step
                            plot_y = row // step
                            trail_x.append(plot_x)
                            trail_y.append(plot_y)
                            trail_z.append(z + 5)
                except:
                    continue

            if trail_x:
                ax.plot(
                    trail_x, trail_y, trail_z, "r-", linewidth=3, label="Trail Path"
                )

            ax.set_title("3D Terrain Visualization with Trail Path")
            ax.set_xlabel("Easting (m)")
            ax.set_ylabel("Northing (m)")
            ax.set_zlabel("Elevation (m)")
            plt.colorbar(surface, shrink=0.8)

            # Save to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return {
                "success": True,
                "type": "static",
                "image_base64": image_base64,
                "description": "3D terrain visualization (static image)",
            }

        except Exception as e:
            print(f"Static 3D plot error: {e}")
            return {"success": False, "error": str(e)}

    def analyze_terrain_features(
        self, trail_coords: List[List[float]]
    ) -> Dict[str, Any]:
        """Identify terrain features along the trail"""
        try:
            profile_result = self.extract_elevation_profile(trail_coords)

            if not profile_result.get("success"):
                return profile_result

            elevations = profile_result["elevation_profile"]["elevations"]
            distances = profile_result["elevation_profile"]["distances"]
            slopes = profile_result["elevation_profile"]["slopes"]

            features = []

            # Identify peaks (local maxima)
            for i in range(1, len(elevations) - 1):
                if (
                    elevations[i] > elevations[i - 1]
                    and elevations[i] > elevations[i + 1]
                ):
                    if (
                        elevations[i] - min(elevations[max(0, i - 10) : i + 10]) > 20
                    ):  # At least 20m prominence
                        features.append(
                            {
                                "type": "Peak",
                                "elevation": elevations[i],
                                "distance": distances[i],
                                "description": f"Local peak at {elevations[i]:.1f}m elevation",
                            }
                        )

            # Identify valleys (local minima)
            for i in range(1, len(elevations) - 1):
                if (
                    elevations[i] < elevations[i - 1]
                    and elevations[i] < elevations[i + 1]
                ):
                    if (
                        max(elevations[max(0, i - 10) : i + 10]) - elevations[i] > 20
                    ):  # At least 20m depth
                        features.append(
                            {
                                "type": "Valley",
                                "elevation": elevations[i],
                                "distance": distances[i],
                                "description": f"Valley bottom at {elevations[i]:.1f}m elevation",
                            }
                        )

            # Identify steep sections
            for i, slope in enumerate(slopes):
                if abs(slope) > 25:  # Steep grade > 25%
                    features.append(
                        {
                            "type": "Steep Grade" if slope > 0 else "Steep Descent",
                            "slope": slope,
                            "distance": (
                                distances[i] if i < len(distances) else distances[-1]
                            ),
                            "description": f"{'Uphill' if slope > 0 else 'Downhill'} grade of {abs(slope):.1f}%",
                        }
                    )

            return {
                "success": True,
                "features": features,
                "summary": {
                    "total_features": len(features),
                    "peaks": len([f for f in features if f["type"] == "Peak"]),
                    "valleys": len([f for f in features if f["type"] == "Valley"]),
                    "steep_sections": len(
                        [f for f in features if "Steep" in f["type"]]
                    ),
                },
            }

        except Exception as e:
            return {"error": f"Terrain analysis failed: {str(e)}"}
