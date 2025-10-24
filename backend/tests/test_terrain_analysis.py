"""
Unit tests for utils/terrain_analysis.py
"""
import pytest
from utils.terrain_analysis import (
    get_trail_weather_exposure,
    calculate_terrain_variety,
    get_terrain_variety_description,
    get_surface_difficulty_multiplier,
    estimate_surface_type_from_terrain,
    calculate_surface_difficulty_score,
    get_weather_exposure_from_score,
)


class TestGetTrailWeatherExposure:
    """Tests for weather exposure calculation"""

    def test_low_elevation_trail(self):
        """Low elevation trail should have low exposure"""
        trail = {"max_elevation": 100}
        result = get_trail_weather_exposure(trail)
        
        assert result["exposure_level"] == "Low"
        assert result["score"] == 1.0

    def test_moderate_elevation_trail(self):
        """Moderate elevation should have moderate exposure"""
        trail = {"max_elevation": 800}
        result = get_trail_weather_exposure(trail)
        
        assert result["exposure_level"] in ["Low-Moderate", "Moderate"]
        assert 1.0 <= result["score"] <= 1.3

    def test_high_elevation_trail(self):
        """High elevation should have high exposure"""
        trail = {"max_elevation": 1500}
        result = get_trail_weather_exposure(trail)
        
        assert result["exposure_level"] == "High"
        assert result["score"] > 1.2

    def test_missing_elevation(self):
        """Should handle missing elevation gracefully"""
        trail = {}
        result = get_trail_weather_exposure(trail)
        
        assert "exposure_level" in result
        assert "score" in result


class TestCalculateTerrainVariety:
    """Tests for terrain variety calculation"""

    def test_flat_terrain(self):
        """Flat terrain should have low variety"""
        elevations = [100, 100, 100, 100, 100]
        result = calculate_terrain_variety(elevations)
        
        assert result < 0.2

    def test_varied_terrain(self):
        """Varied terrain should have high variety score"""
        elevations = [100, 150, 120, 180, 110, 200, 130, 190]
        result = calculate_terrain_variety(elevations)
        
        assert result > 0.5

    def test_steady_climb(self):
        """Steady climb should have moderate variety"""
        elevations = [100, 120, 140, 160, 180, 200]
        result = calculate_terrain_variety(elevations)
        
        assert 0.2 < result < 0.6

    def test_empty_elevations(self):
        """Empty elevations should return 0"""
        result = calculate_terrain_variety([])
        assert result == 0

    def test_single_elevation(self):
        """Single elevation should return 0"""
        result = calculate_terrain_variety([100])
        assert result == 0


class TestGetTerrainVarietyDescription:
    """Tests for terrain variety descriptions"""

    def test_low_variety(self):
        """Low variety score should return appropriate description"""
        result = get_terrain_variety_description(0.15)
        assert "gentle" in result.lower() or "gradual" in result.lower()

    def test_moderate_variety(self):
        """Moderate variety score"""
        result = get_terrain_variety_description(0.45)
        assert "moderate" in result.lower() or "varied" in result.lower()

    def test_high_variety(self):
        """High variety score"""
        result = get_terrain_variety_description(0.75)
        assert "highly varied" in result.lower() or "challenging" in result.lower()

    def test_extreme_variety(self):
        """Extreme variety score"""
        result = get_terrain_variety_description(0.95)
        assert "extreme" in result.lower() or "technical" in result.lower()


class TestGetSurfaceDifficultyMultiplier:
    """Tests for surface difficulty multipliers"""

    def test_paved_surface(self):
        """Paved surface should have lowest multiplier"""
        result = get_surface_difficulty_multiplier("paved")
        assert result == 1.0

    def test_trail_surface(self):
        """Trail surface should have moderate multiplier"""
        result = get_surface_difficulty_multiplier("trail")
        assert 1.0 < result < 1.5

    def test_technical_surface(self):
        """Technical surface should have high multiplier"""
        result = get_surface_difficulty_multiplier("technical")
        assert result > 1.5

    def test_unknown_surface(self):
        """Unknown surface should have default multiplier"""
        result = get_surface_difficulty_multiplier("unknown_surface")
        assert result >= 1.0


class TestEstimateSurfaceTypeFromTerrain:
    """Tests for surface type estimation"""

    def test_flat_coordinates(self):
        """Flat terrain should estimate easier surface"""
        coordinates = [
            [-27.4705, 152.9629],
            [-27.4710, 152.9630],
            [-27.4715, 152.9631],
        ]
        result = estimate_surface_type_from_terrain(coordinates)
        
        assert "surface_type" in result
        assert isinstance(result["surface_type"], str)

    def test_with_elevation_profile(self):
        """Should use elevation profile if provided"""
        coordinates = [[-27.4705, 152.9629], [-27.4710, 152.9635]]
        elevation_profile = [
            {"distance": 0.0, "elevation": 100},
            {"distance": 1.0, "elevation": 150},
        ]
        result = estimate_surface_type_from_terrain(coordinates, elevation_profile)
        
        assert "surface_type" in result
        assert "confidence" in result


class TestCalculateSurfaceDifficultyScore:
    """Tests for surface difficulty scoring"""

    def test_all_paved_segments(self):
        """All paved segments should have low score"""
        segments = [
            {"surface_type": "paved", "length": 1.0},
            {"surface_type": "paved", "length": 1.0},
        ]
        result = calculate_surface_difficulty_score(segments)
        
        assert result < 2.0

    def test_mixed_surface_segments(self):
        """Mixed surfaces should have moderate score"""
        segments = [
            {"surface_type": "paved", "length": 1.0},
            {"surface_type": "trail", "length": 1.0},
            {"surface_type": "technical", "length": 1.0},
        ]
        result = calculate_surface_difficulty_score(segments)
        
        assert 2.0 < result < 8.0

    def test_empty_segments(self):
        """Empty segments should return default score"""
        result = calculate_surface_difficulty_score([])
        assert result >= 0


class TestGetWeatherExposureFromScore:
    """Tests for weather exposure score conversion"""

    def test_low_score(self):
        """Low score should return Low exposure"""
        result = get_weather_exposure_from_score(1.0)
        assert result == "Low"

    def test_moderate_score(self):
        """Moderate score should return appropriate level"""
        result = get_weather_exposure_from_score(1.2)
        assert result in ["Low-Moderate", "Moderate"]

    def test_high_score(self):
        """High score should return High exposure"""
        result = get_weather_exposure_from_score(1.35)
        assert result == "High"

    def test_invalid_score(self):
        """Should handle invalid scores gracefully"""
        result = get_weather_exposure_from_score(-1.0)
        assert isinstance(result, str)
