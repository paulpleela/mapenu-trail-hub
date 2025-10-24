"""
Unit tests for API routes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    return TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root_returns_200(self, client):
        """Root endpoint should return 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_json(self, client):
        """Root endpoint should return JSON"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data

    def test_root_shows_features(self, client):
        """Root endpoint should show available features"""
        response = client.get("/")
        data = response.json()
        assert "features" in data
        assert isinstance(data["features"], dict)


class TestTrailsEndpoint:
    """Tests for /trails endpoint"""

    @patch("routes.trails.supabase")
    def test_get_trails_success(self, mock_supabase, client):
        """Should return trails list successfully"""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "name": "Test Trail",
                "distance": 5.5,
                "elevation_gain": 250,
                "difficulty_level": "Moderate",
            }
        ]
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        response = client.get("/trails")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "trails" in data

    @patch("routes.trails.supabase")
    def test_get_trails_empty(self, mock_supabase, client):
        """Should handle empty trails list"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

        response = client.get("/trails")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["trails"]) == 0


class TestAnalyticsEndpoint:
    """Tests for /analytics/overview endpoint"""

    @patch("routes.trails.supabase")
    def test_analytics_success(self, mock_supabase, client):
        """Should return analytics data"""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "distance": 5.0,
                "elevation_gain": 200,
                "difficulty_level": "Moderate",
                "difficulty_score": 6.5,
            },
            {
                "id": 2,
                "distance": 10.0,
                "elevation_gain": 500,
                "difficulty_level": "Hard",
                "difficulty_score": 8.5,
            },
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response

        response = client.get("/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "total_trails" in data
        assert "total_distance_km" in data
        assert "difficulty_distribution" in data

    @patch("routes.trails.supabase")
    def test_analytics_empty_database(self, mock_supabase, client):
        """Should handle empty database gracefully"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response

        response = client.get("/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_trails"] == 0


class TestElevationSourcesEndpoint:
    """Tests for /trail/{trail_id}/elevation-sources endpoint"""

    @patch("routes.analysis.supabase")
    def test_elevation_sources_invalid_trail(self, mock_supabase, client):
        """Should return 404 for invalid trail ID"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        response = client.get("/trail/99999/elevation-sources")
        assert response.status_code == 404

    @patch("routes.analysis.supabase")
    @patch("routes.analysis.app_state.get_dem_analyzer")
    @patch("routes.analysis.app_state.get_lidar_extractor")
    def test_elevation_sources_success(
        self, mock_lidar, mock_dem, mock_supabase, client
    ):
        """Should return elevation sources for valid trail"""
        # Mock trail data
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "name": "Test Trail",
                "coordinates": [[-27.4705, 152.9629], [-27.4710, 152.9635]],
                "elevation_profile": [
                    {"distance": 0.0, "elevation": 100},
                    {"distance": 1.0, "elevation": 110},
                ],
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        # Mock DEM analyzer
        mock_dem.return_value = None
        mock_lidar.return_value = None

        response = client.get("/trail/1/elevation-sources")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "sources" in data


class TestSimilarTrailsEndpoint:
    """Tests for /trail/{trail_id}/similar endpoint"""

    @patch("routes.trails.supabase")
    def test_similar_trails_invalid_trail(self, mock_supabase, client):
        """Should return 404 for invalid trail ID"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        response = client.get("/trail/99999/similar")
        assert response.status_code == 404

    @patch("routes.trails.supabase")
    @patch("routes.trails.calculate_trail_similarity")
    def test_similar_trails_success(self, mock_similarity, mock_supabase, client):
        """Should return similar trails"""
        # Mock target trail
        mock_response_target = MagicMock()
        mock_response_target.data = [
            {
                "id": 1,
                "name": "Target Trail",
                "distance": 5.0,
                "elevation_gain": 200,
                "difficulty_score": 6.5,
            }
        ]

        # Mock all trails
        mock_response_all = MagicMock()
        mock_response_all.data = [
            {
                "id": 1,
                "name": "Target Trail",
                "distance": 5.0,
                "elevation_gain": 200,
                "difficulty_score": 6.5,
            },
            {
                "id": 2,
                "name": "Similar Trail",
                "distance": 5.5,
                "elevation_gain": 220,
                "difficulty_score": 6.8,
            },
        ]

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response_target
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response_all
        mock_similarity.return_value = 0.85

        response = client.get("/trail/1/similar")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "similar_trails" in data


class TestDeleteTrailEndpoint:
    """Tests for DELETE /trail/{trail_id} endpoint"""

    @patch("routes.trails.supabase")
    def test_delete_trail_success(self, mock_supabase, client):
        """Should successfully delete a trail"""
        mock_response = MagicMock()
        mock_response.data = [{"id": 1}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response

        response = client.delete("/trail/1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("routes.trails.supabase")
    def test_delete_trail_not_found(self, mock_supabase, client):
        """Should return 404 for non-existent trail"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

        response = client.delete("/trail/99999")
        assert response.status_code == 404
