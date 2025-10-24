"""
Utility modules for MAPENU backend.
"""
from .calculations import (
    haversine,
    count_rolling_hills,
    analyze_rolling_hills,
    calculate_trail_similarity
)
from .terrain_analysis import (
    get_trail_weather_exposure,
    calculate_terrain_variety,
    get_terrain_variety_description,
    get_surface_difficulty_multiplier,
    estimate_surface_type_from_terrain,
    calculate_surface_difficulty_score,
    get_surface_difficulty_description,
    get_weather_exposure_from_score
)
from .dem_processing import (
    find_relevant_dem_tiles,
    process_dem_for_trail
)

__all__ = [
    'haversine',
    'count_rolling_hills',
    'analyze_rolling_hills',
    'calculate_trail_similarity',
    'get_trail_weather_exposure',
    'calculate_terrain_variety',
    'get_terrain_variety_description',
    'get_surface_difficulty_multiplier',
    'estimate_surface_type_from_terrain',
    'calculate_surface_difficulty_score',
    'get_surface_difficulty_description',
    'get_weather_exposure_from_score',
    'find_relevant_dem_tiles',
    'process_dem_for_trail'
]
