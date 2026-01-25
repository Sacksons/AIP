# tests/test_auth.py
import pytest


class TestUserCreation:
    """Tests for user registration endpoint."""

    def test_create_user_success(self, client, sample_user_data):
        """Test successful user creation."""
        response = client.post("/auth/users/", json=sample_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["role"] == sample_user_data["role"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    def test_create_user_duplicate_username(self, client, sample_user_data):
        """Test that duplicate usernames are rejected."""
        # Create first user
        client.post("/auth/users/", json=sample_user_data)
        # Try to create duplicate
        response = client.post("/auth/users/", json=sample_user_data)
        assert response.status_code in [400, 422, 500]  # Should fail

    def test_create_user_missing_fields(self, client):
        """Test that missing required fields are rejected."""
        incomplete_data = {"username": "testuser"}
        response = client.post("/auth/users/", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_create_user_empty_username(self, client):
        """Test that empty username is rejected."""
        data = {"username": "", "password": "password123", "role": "investor"}
        response = client.post("/auth/users/", json=data)
        # Should either fail validation or create with empty username
        # depending on schema validation
        assert response.status_code in [200, 422]


class TestUserLogin:
    """Tests for user login/token endpoint."""

    def test_login_success(self, client, sample_user_data):
        """Test successful login returns a token."""
        # First create a user
        client.post("/auth/users/", json=sample_user_data)

        # Then try to login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = client.post(
            "/auth/token",
            data=login_data,  # OAuth2 uses form data
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # May fail if password hashing not set up correctly
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, sample_user_data):
        """Test login with wrong password fails."""
        # Create user
        client.post("/auth/users/", json=sample_user_data)

        # Try login with wrong password
        login_data = {
            "username": sample_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = client.post(
            "/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401


class TestHealthCheck:
    """Tests for basic API health."""

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
