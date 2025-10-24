"""
Terrain analysis functions for weather exposure, surface types, and difficulty.
"""


def get_trail_weather_exposure(trail):
    """
    Calculate static weather exposure risk based on elevation.
    (doesn't change with current weather)
    
    Args:
        trail: Trail dict with max_elevation
    
    Returns:
        dict: exposure_level and risk_factors
    """
    max_elev = trail.get("max_elevation", 0)

    # Return exposure level and explanation (static characteristics)
    if max_elev > 1500:
        return {
            "exposure_level": "High",
            "risk_factors": [
                "Rapid weather changes",
                "Snow/ice risk",
                "High wind exposure",
                "Temperature drops",
            ],
        }
    elif max_elev > 1000:
        return {
            "exposure_level": "Moderate",
            "risk_factors": ["Cooler temperatures", "Wind exposure", "Potential fog"],
        }
    elif max_elev > 500:
        return {
            "exposure_level": "Low-Moderate",
            "risk_factors": ["Slightly cooler temps", "Some wind exposure"],
        }
    else:
        return {
            "exposure_level": "Low",
            "risk_factors": ["Minimal weather impact", "Protected terrain"],
        }


def calculate_terrain_variety(elevations):
    """
    Calculate how varied the terrain is (0-10 scale).
    
    Args:
        elevations: List of elevation values in meters
    
    Returns:
        int: Variety score 0-10
    """
    if len(elevations) < 10:
        return 0

    # Calculate elevation ranges in 100m bands
    elevation_bands = set()
    for elev in elevations:
        band = int(elev / 100) * 100  # Round to nearest 100m
        elevation_bands.add(band)

    # More bands = more variety
    variety_score = min(len(elevation_bands), 10)  # Cap at 10

    # Also consider elevation change rate
    elevation_changes = []
    for i in range(1, len(elevations)):
        change_rate = abs(elevations[i] - elevations[i - 1])
        elevation_changes.append(change_rate)

    # Bonus for frequent elevation changes
    if elevation_changes:
        avg_change = sum(elevation_changes) / len(elevation_changes)
        if avg_change > 20:  # Frequent significant changes
            variety_score = min(variety_score + 2, 10)
        elif avg_change > 10:  # Moderate changes
            variety_score = min(variety_score + 1, 10)

    return variety_score


def get_terrain_variety_description(score):
    """
    Get a human-readable description for terrain variety score.
    
    Args:
        score: Variety score 0-10
    
    Returns:
        str: Description of terrain variety
    """
    if score >= 8:
        return "Highly varied terrain with multiple elevation zones"
    elif score >= 6:
        return "Good terrain variety with several elevation changes"
    elif score >= 4:
        return "Moderate terrain variety with some elevation changes"
    elif score >= 2:
        return "Limited terrain variety, mostly consistent elevation"
    else:
        return "Flat or very consistent terrain"


def get_surface_difficulty_multiplier(surface_type):
    """
    Get difficulty multiplier based on terrain surface type.
    
    Surface difficulty scale:
    - Easy (0.7-0.8x): Paved roads, boardwalks, concrete
    - Normal (1.0x): Dirt trails, gravel, grass (baseline)
    - Moderate (1.1-1.3x): Soil, forest floor, wood chips, tall grass
    - Challenging (1.3-1.6x): Sand, mud, loose gravel, scree, snow
    - Difficult (1.6-2.0x): Rock, boulders, swamp, ice
    
    Args:
        surface_type: String describing surface type
    
    Returns:
        float: Difficulty multiplier
    """
    surface_multipliers = {
        # Easy surfaces (< 1.0)
        "paved": 0.7,
        "boardwalk": 0.8,
        "concrete": 0.75,
        # Normal surfaces (1.0)
        "dirt": 1.0,
        "gravel": 1.0,
        "grass": 1.0,
        # Moderate surfaces (1.1-1.3)
        "soil": 1.1,
        "forest_floor": 1.15,
        "crushed_stone": 1.1,
        "wood_chips": 1.2,
        "tall_grass": 1.25,
        # Challenging surfaces (1.3-1.6)
        "sand": 1.4,
        "mud": 1.5,
        "loose_gravel": 1.3,
        "scree": 1.6,
        "snow": 1.4,
        # Difficult surfaces (1.6-2.0)
        "rock": 1.7,
        "boulder": 1.8,
        "swamp": 1.9,
        "ice": 2.0,
        # Default for unknown
        "unknown": 1.0,
    }

    return surface_multipliers.get(surface_type.lower(), 1.0)


def estimate_surface_type_from_terrain(coordinates, elevation_profile=None):
    """
    Estimate likely surface types based on terrain characteristics.
    (Simplified estimation - in production would use satellite data or trail databases)
    
    Args:
        coordinates: List of [lat, lon] coordinates
        elevation_profile: Optional list of elevation dicts
    
    Returns:
        list: Surface segments with type and percentage
    """
    if not coordinates:
        return [{"surface": "unknown", "percentage": 100}]

    surface_segments = []

    # Get elevation statistics if available
    elevations = []
    if elevation_profile:
        elevations = [point.get("elevation", 0) for point in elevation_profile]

    # Estimate based on coordinate patterns and elevation
    if elevations:
        avg_elevation = sum(elevations) / len(elevations)
        elevation_variance = sum((e - avg_elevation) ** 2 for e in elevations) / len(
            elevations
        )

        # High elevation, high variance = rocky terrain
        if avg_elevation > 800 and elevation_variance > 1000:
            surface_segments = [
                {"surface": "rock", "percentage": 40},
                {"surface": "dirt", "percentage": 35},
                {"surface": "scree", "percentage": 25},
            ]
        # High elevation, low variance = alpine meadows
        elif avg_elevation > 800:
            surface_segments = [
                {"surface": "grass", "percentage": 50},
                {"surface": "dirt", "percentage": 30},
                {"surface": "rock", "percentage": 20},
            ]
        # Medium elevation, high variance = forest trails
        elif avg_elevation > 200 and elevation_variance > 500:
            surface_segments = [
                {"surface": "forest_floor", "percentage": 60},
                {"surface": "dirt", "percentage": 30},
                {"surface": "soil", "percentage": 10},
            ]
        # Low elevation, coastal areas
        elif avg_elevation < 100:
            surface_segments = [
                {"surface": "dirt", "percentage": 50},
                {"surface": "sand", "percentage": 30},
                {"surface": "grass", "percentage": 20},
            ]
        else:
            # Default mixed terrain
            surface_segments = [
                {"surface": "dirt", "percentage": 70},
                {"surface": "gravel", "percentage": 20},
                {"surface": "grass", "percentage": 10},
            ]
    else:
        # No elevation data, assume mixed terrain
        surface_segments = [
            {"surface": "dirt", "percentage": 60},
            {"surface": "gravel", "percentage": 25},
            {"surface": "grass", "percentage": 15},
        ]

    return surface_segments


def calculate_surface_difficulty_score(surface_segments):
    """
    Calculate overall surface difficulty score from surface segments.
    
    Args:
        surface_segments: List of dicts with surface type and percentage
    
    Returns:
        float: Weighted average difficulty multiplier
    """
    if not surface_segments:
        return 1.0

    total_score = 0
    total_percentage = 0

    for segment in surface_segments:
        surface = segment.get("surface", "unknown")
        percentage = segment.get("percentage", 0)
        multiplier = get_surface_difficulty_multiplier(surface)

        total_score += multiplier * percentage
        total_percentage += percentage

    if total_percentage == 0:
        return 1.0

    # Weighted average of surface difficulties
    return total_score / total_percentage


def get_surface_difficulty_description(score, surface_segments):
    """
    Get human-readable description of surface difficulty.
    
    Args:
        score: Difficulty multiplier score
        surface_segments: List of surface segment dicts
    
    Returns:
        str: Formatted description
    """
    primary_surfaces = sorted(
        surface_segments, key=lambda x: x["percentage"], reverse=True
    )[:2]

    description = f"Surface difficulty: {score:.2f}x baseline. "

    if score <= 0.8:
        description += "Very easy walking on "
    elif score <= 1.0:
        description += "Standard trail surface with "
    elif score <= 1.3:
        description += "Moderately challenging surface with "
    elif score <= 1.6:
        description += "Difficult surface requiring careful footing with "
    else:
        description += "Very challenging surface demanding experience with "

    surface_names = []
    for surface in primary_surfaces:
        name = surface["surface"].replace("_", " ")
        percentage = surface["percentage"]
        surface_names.append(f"{name} ({percentage}%)")

    description += " and ".join(surface_names)

    return description


def get_weather_exposure_from_score(score):
    """
    Convert weather score back to exposure level and risk factors.
    
    Args:
        score: Weather exposure score (1.0 = baseline)
    
    Returns:
        dict: exposure_level and risk_factors
    """
    # Handle None/null values
    if score is None:
        score = 1.0  # Default to low exposure

    try:
        score = float(score)  # Ensure it's a number
    except (ValueError, TypeError):
        score = 1.0  # Default to low exposure if conversion fails

    if score >= 1.25:
        return {
            "exposure_level": "High",
            "risk_factors": [
                "Rapid weather changes",
                "Snow/ice risk",
                "High wind exposure",
                "Temperature drops",
            ],
        }
    elif score >= 1.15:
        return {
            "exposure_level": "Moderate",
            "risk_factors": ["Cooler temperatures", "Wind exposure", "Potential fog"],
        }
    elif score >= 1.05:
        return {
            "exposure_level": "Low-Moderate",
            "risk_factors": ["Slightly cooler temps", "Some wind exposure"],
        }
    else:
        return {
            "exposure_level": "Low",
            "risk_factors": ["Minimal weather impact", "Protected terrain"],
        }
