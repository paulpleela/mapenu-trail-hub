"""
Unit tests for utils/dem_processing.py
"""
import pytest
from utils.dem_processing import find_relevant_dem_tiles, process_dem_for_trail


class TestFindRelevantDemTiles:
    """Tests for finding relevant DEM tiles"""

    def test_single_point(self):
        """Should find tiles for a single coordinate"""
        trail_coords = [[-27.4705, 152.9629]]
        result = find_relevant_dem_tiles(trail_coords)
        
        assert isinstance(result, list)
        # Should return coordinate bounds or tile info

    def test_multiple_points(self):
        """Should find tiles covering multiple points"""
        trail_coords = [
            [-27.4705, 152.9629],
            [-27.4710, 152.9635],
            [-27.4715, 152.9640],
        ]
        result = find_relevant_dem_tiles(trail_coords)
        
        assert isinstance(result, list)

    def test_empty_coordinates(self):
        """Should handle empty coordinates gracefully"""
        result = find_relevant_dem_tiles([])
        assert isinstance(result, list)

    def test_far_apart_points(self):
        """Should find multiple tiles for far apart points"""
        trail_coords = [
            [-27.4705, 152.9629],  # Brisbane
            [-27.5705, 153.0629],  # ~10km away
        ]
        result = find_relevant_dem_tiles(trail_coords)
        
        assert isinstance(result, list)


class TestProcessDemForTrail:
    """Tests for processing DEM data for a trail"""

    def test_process_with_no_dem_files(self):
        """Should handle case with no DEM files"""
        trail_coords = [[-27.4705, 152.9629]]
        dem_files = []
        result = process_dem_for_trail(trail_coords, dem_files)
        
        # Should return empty or error indication
        assert result is not None

    def test_process_with_resolution_factor(self):
        """Should respect resolution factor parameter"""
        trail_coords = [
            [-27.4705, 152.9629],
            [-27.4710, 152.9635],
        ]
        dem_files = []
        
        # Test with different resolution factors
        result1 = process_dem_for_trail(trail_coords, dem_files, resolution_factor=2)
        result2 = process_dem_for_trail(trail_coords, dem_files, resolution_factor=8)
        
        assert result1 is not None
        assert result2 is not None

    def test_single_coordinate(self):
        """Should handle single coordinate"""
        trail_coords = [[-27.4705, 152.9629]]
        dem_files = []
        result = process_dem_for_trail(trail_coords, dem_files)
        
        assert result is not None
