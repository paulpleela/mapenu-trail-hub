"""
Mathematical calculations and trail analysis functions.
"""
import math


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: First point coordinates (degrees)
        lat2, lon2: Second point coordinates (degrees)
    
    Returns:
        float: Distance in meters
    """
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def count_rolling_hills(elevations):
    """
    Count the number of distinct "hills" (peaks and valleys) in the elevation profile.

    Algorithm:
    1. Identify all local peaks (higher than neighbors)
    2. Identify all local valleys (lower than neighbors)
    3. Total hills = peaks + valleys (each represents a direction change)

    A "significant" peak/valley must have at least 1m elevation difference from neighbors
    to filter out GPS noise.

    Args:
        elevations: List of elevation values in meters

    Returns:
        int: Number of distinct hills (peaks + valleys)
    """
    if len(elevations) < 3:
        return 0

    # Minimum elevation change to be considered significant
    # 1m threshold catches most noticeable hills while filtering extreme GPS noise
    min_prominence = 1.0  # meters

    peaks = 0
    valleys = 0

    for i in range(1, len(elevations) - 1):
        prev_elev = elevations[i - 1]
        curr_elev = elevations[i]
        next_elev = elevations[i + 1]

        # Check if this is a local peak (higher than both neighbors)
        if curr_elev > prev_elev and curr_elev > next_elev:
            # Check if it's significant enough
            if (curr_elev - prev_elev >= min_prominence) or (
                curr_elev - next_elev >= min_prominence
            ):
                peaks += 1

        # Check if this is a local valley (lower than both neighbors)
        elif curr_elev < prev_elev and curr_elev < next_elev:
            # Check if it's significant enough
            if (prev_elev - curr_elev >= min_prominence) or (
                next_elev - curr_elev >= min_prominence
            ):
                valleys += 1

    # Total number of hills = peaks + valleys
    # Each represents a change in terrain direction
    total_hills = peaks + valleys

    return total_hills


def analyze_rolling_hills(elevations, distances):
    """
    Advanced rolling hills analysis: counts and scores significant ascents/descents.
    
    Measures trail 'bumpiness' with:
    - frequency 60%
    - amplitude 40%

    Args:
        elevations: List of elevation values in meters
        distances: List of cumulative distances in kilometers

    Returns:
        tuple: (rolling_index: float, hills_count: int)
    """
    if len(elevations) < 3:
        return 0.0, 0

    # Count actual hills (peaks and valleys)
    hills_count = count_rolling_hills(elevations)

    # For the rolling index calculation, count significant elevation changes
    threshold = 1  # meters, what counts as a significant change
    significant_changes = []
    for i in range(1, len(elevations)):
        change = elevations[i] - elevations[i - 1]
        if abs(change) >= threshold:
            significant_changes.append(abs(change))

    # Frequency: how many significant changes per km
    total_distance = distances[-1] if distances else 1
    changes_per_km = (
        len(significant_changes) / total_distance if total_distance > 0 else 0
    )

    # Amplitude: average size of significant changes
    avg_change_size = (
        sum(significant_changes) / len(significant_changes)
        if significant_changes
        else 0
    )

    # Composite index: weighted sum (60% frequency, 40% amplitude)
    rolling_index = 0.6 * changes_per_km + 0.4 * (
        avg_change_size / 20
    )  # typical big hills are ~20 m per hill

    # Debug output
    print(f"🔍 Rolling Hills Debug:")
    print(f"   - Actual hills (peaks + valleys): {hills_count}")
    print(f"   - Significant elevation changes: {len(significant_changes)}")
    print(f"   - Total distance: {total_distance:.2f} km")
    print(f"   - Changes per km: {changes_per_km:.2f}")
    print(f"   - Avg change size: {avg_change_size:.2f} m")
    print(f"   - Rolling index (UNCAPPED): {rolling_index:.4f}")

    # Return both the rolling index and the count
    return rolling_index, hills_count


def calculate_trail_similarity(trail1, trail2):
    """
    Calculate similarity score between two trails (0-1, higher = more similar).
    
    Weights 5 checks:
    - distance difference within ±1 km (25%),
    - elevation-gain difference within ±500 m (25%),
    - overall difficulty within ±5 on our 10-point scale (20%),
    - terrain character using the rolling-hills index (15%),
    - and surface difficulty similarity (15%).
    
    Args:
        trail1: First trail dict with metrics
        trail2: Second trail dict with metrics
    
    Returns:
        float: Similarity score between 0 and 1
    """
    # Normalize factors for comparison
    distance_diff = abs(trail1["distance"] - trail2["distance"])
    distance_similarity = max(
        0, 1 - (distance_diff / 1000)
    )  # Within 1km is very similar

    elevation_gain_diff = abs(trail1["elevation_gain"] - trail2["elevation_gain"])
    elevation_similarity = max(
        0, 1 - (elevation_gain_diff / 500)
    )  # Within 500m is similar

    difficulty_diff = abs(trail1["difficulty_score"] - trail2["difficulty_score"])
    difficulty_similarity = max(
        0, 1 - (difficulty_diff / 5)
    )  # Within 5 points is similar

    rolling_hills_diff = abs(
        trail1["rolling_hills_index"] - trail2["rolling_hills_index"]
    )
    rolling_similarity = max(0, 1 - (rolling_hills_diff / 0.5))  # Within 0.5 is similar

    # Surface difficulty similarity
    surface1 = trail1.get("surface_difficulty_score", 1.0)
    surface2 = trail2.get("surface_difficulty_score", 1.0)
    surface_diff = abs(surface1 - surface2)
    surface_similarity = max(
        0, 1 - (surface_diff / 0.5)
    )  # Within 0.5 multiplier is similar

    # Weighted average
    similarity = (
        distance_similarity * 0.25
        + elevation_similarity * 0.25
        + difficulty_similarity * 0.20
        + rolling_similarity * 0.15
        + surface_similarity * 0.15
    )

    return similarity
