# tests/test_main.py
"""
Basic API tests for the main application.
"""
import pytest


class TestAPIRoot:
    """Tests for root API endpoints."""

    def test_health_check(self, client):
        """Test the health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_invalid_endpoint(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
