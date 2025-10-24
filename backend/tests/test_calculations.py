"""
Unit tests for utils/calculations.py
"""
import pytest
from utils.calculations import (
    haversine,
    count_rolling_hills,
    analyze_rolling_hills,
    calculate_trail_similarity,
)


class TestHaversine:
    """Tests for haversine distance calculation"""

    def test_same_point(self):
        """Distance between same point should be 0"""
        result = haversine(-27.4705, 152.9629, -27.4705, 152.9629)
        assert result == 0.0

    def test_known_distance(self):
        """Test with known distance (approx 1km)"""
        # Brisbane CBD to South Bank (approx 1.2 km)
        result = haversine(-27.4705, 152.9629, -27.4815, 152.9690)
        assert 1.0 < result < 1.5

    def test_different_hemispheres(self):
        """Test points in different hemispheres"""
        # North America to Australia
        result = haversine(40.7128, -74.0060, -33.8688, 151.2093)
        assert result > 15000  # Should be over 15,000 km


class TestCountRollingHills:
    """Tests for rolling hills counting"""

    def test_flat_terrain(self):
        """Flat terrain should have minimal rolling hills"""
        elevations = [100, 100, 100, 100, 100]
        result = count_rolling_hills(elevations)
        assert result["rolling_hills_index"] < 0.1
        assert result["rolling_hills_count"] == 0

    def test_steady_climb(self):
        """Steady climb should have low rolling hills index"""
        elevations = [100, 110, 120, 130, 140, 150]
        result = count_rolling_hills(elevations)
        assert result["rolling_hills_index"] < 0.2
        assert result["rolling_hills_count"] == 0

    def test_rolling_terrain(self):
        """Rolling terrain should be detected"""
        elevations = [100, 120, 110, 130, 115, 135, 120, 140]
        result = count_rolling_hills(elevations)
        assert result["rolling_hills_index"] > 0.3
        assert result["rolling_hills_count"] > 0

    def test_empty_elevations(self):
        """Empty elevation list should return zero values"""
        result = count_rolling_hills([])
        assert result["rolling_hills_index"] == 0
        assert result["rolling_hills_count"] == 0

    def test_single_elevation(self):
        """Single elevation should return zero values"""
        result = count_rolling_hills([100])
        assert result["rolling_hills_index"] == 0
        assert result["rolling_hills_count"] == 0


class TestAnalyzeRollingHills:
    """Tests for detailed rolling hills analysis"""

    def test_flat_terrain_analysis(self):
        """Flat terrain analysis"""
        elevations = [100, 100, 100, 100, 100]
        distances = [0, 0.5, 1.0, 1.5, 2.0]
        result = analyze_rolling_hills(elevations, distances)
        
        assert result["rolling_hills_index"] < 0.1
        assert result["rolling_hills_count"] == 0
        assert result["total_elevation_changes"] == 0
        assert len(result["segments"]) > 0

    def test_rolling_terrain_analysis(self):
        """Rolling terrain with multiple ups and downs"""
        elevations = [100, 120, 110, 130, 115, 135, 120]
        distances = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        result = analyze_rolling_hills(elevations, distances)
        
        assert result["rolling_hills_index"] > 0.2
        assert result["rolling_hills_count"] > 0
        assert result["total_elevation_changes"] > 0

    def test_mismatched_lengths(self):
        """Should handle mismatched elevation and distance lengths"""
        elevations = [100, 110, 120]
        distances = [0, 0.5]
        result = analyze_rolling_hills(elevations, distances)
        
        # Should still return valid results
        assert "rolling_hills_index" in result
        assert "rolling_hills_count" in result


class TestCalculateTrailSimilarity:
    """Tests for trail similarity calculation"""

    def test_identical_trails(self):
        """Identical trails should have similarity close to 1.0"""
        trail1 = {
            "distance": 5.0,
            "elevation_gain": 200,
            "difficulty_score": 6.5,
            "rolling_hills_index": 0.5,
        }
        trail2 = {
            "distance": 5.0,
            "elevation_gain": 200,
            "difficulty_score": 6.5,
            "rolling_hills_index": 0.5,
        }
        result = calculate_trail_similarity(trail1, trail2)
        assert result > 0.95

    def test_completely_different_trails(self):
        """Completely different trails should have low similarity"""
        trail1 = {
            "distance": 2.0,
            "elevation_gain": 50,
            "difficulty_score": 2.0,
            "rolling_hills_index": 0.1,
        }
        trail2 = {
            "distance": 20.0,
            "elevation_gain": 1000,
            "difficulty_score": 9.0,
            "rolling_hills_index": 0.9,
        }
        result = calculate_trail_similarity(trail1, trail2)
        assert result < 0.3

    def test_similar_trails(self):
        """Similar trails should have moderate similarity"""
        trail1 = {
            "distance": 5.0,
            "elevation_gain": 200,
            "difficulty_score": 6.5,
            "rolling_hills_index": 0.5,
        }
        trail2 = {
            "distance": 5.5,
            "elevation_gain": 220,
            "difficulty_score": 6.8,
            "rolling_hills_index": 0.55,
        }
        result = calculate_trail_similarity(trail1, trail2)
        assert 0.8 < result < 0.95

    def test_missing_fields(self):
        """Should handle missing fields gracefully"""
        trail1 = {"distance": 5.0}
        trail2 = {"distance": 5.5}
        result = calculate_trail_similarity(trail1, trail2)
        
        # Should still return a valid number between 0 and 1
        assert 0 <= result <= 1
