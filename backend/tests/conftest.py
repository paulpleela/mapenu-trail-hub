"""
Test configuration and fixtures for pytest
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    mock = MagicMock()
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.delete.return_value = mock
    mock.execute.return_value = MagicMock(data=[])
    return mock


@pytest.fixture
def sample_trail_data():
    """Sample trail data for testing"""
    return {
        "id": 1,
        "name": "Test Trail",
        "distance": 5.5,
        "elevation_gain": 250,
        "elevation_loss": 230,
        "max_elevation": 500,
        "min_elevation": 250,
        "difficulty_score": 6.5,
        "difficulty_level": "Moderate",
        "max_slope": 15.5,
        "avg_slope": 8.2,
        "rolling_hills_index": 0.45,
        "rolling_hills_count": 3,
        "terrain_variety_score": 0.65,
        "technical_rating": 5.5,
        "weather_difficulty_multiplier": 1.2,
        "coordinates": [
            [-27.4705, 152.9629],
            [-27.4710, 152.9635],
            [-27.4715, 152.9640],
        ],
        "elevation_profile": [
            {"distance": 0.0, "elevation": 250},
            {"distance": 2.5, "elevation": 400},
            {"distance": 5.5, "elevation": 500},
        ],
    }


@pytest.fixture
def sample_elevations():
    """Sample elevation data for testing"""
    return [100, 110, 105, 120, 115, 130, 125, 140, 135, 150]


@pytest.fixture
def sample_coordinates():
    """Sample GPS coordinates for testing"""
    return [
        [-27.4705, 152.9629],
        [-27.4710, 152.9635],
        [-27.4715, 152.9640],
        [-27.4720, 152.9645],
        [-27.4725, 152.9650],
    ]
