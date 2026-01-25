# tests/test_investors.py
import pytest


class TestCreateInvestor:
    """Tests for investor creation endpoint."""

    def test_create_investor_success(self, client, sample_investor_data):
        """Test successful investor creation."""
        response = client.post("/investors/", json=sample_investor_data)
        assert response.status_code == 200
        data = response.json()
        assert data["fund_name"] == sample_investor_data["fund_name"]
        assert data["aum"] == sample_investor_data["aum"]
        assert data["ticket_size_min"] == sample_investor_data["ticket_size_min"]
        assert data["ticket_size_max"] == sample_investor_data["ticket_size_max"]
        assert "id" in data

    def test_create_investor_minimal_data(self, client):
        """Test creating investor with only required fields."""
        minimal_data = {
            "fund_name": "Minimal Fund",
            "ticket_size_min": 500000.0,
            "ticket_size_max": 10000000.0,
            "instruments": ["Equity"],
            "country_focus": ["Kenya"],
            "sector_focus": ["Energy"]
        }
        response = client.post("/investors/", json=minimal_data)
        assert response.status_code == 200
        data = response.json()
        assert data["fund_name"] == "Minimal Fund"
        assert data["aum"] is None  # Optional field

    def test_create_investor_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        incomplete_data = {"fund_name": "Incomplete Fund"}
        response = client.post("/investors/", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_create_investor_invalid_instrument(self, client):
        """Test that invalid instrument values are rejected."""
        invalid_data = {
            "fund_name": "Invalid Fund",
            "ticket_size_min": 500000.0,
            "ticket_size_max": 10000000.0,
            "instruments": ["InvalidInstrument"],
            "country_focus": ["Kenya"],
            "sector_focus": ["Energy"]
        }
        response = client.post("/investors/", json=invalid_data)
        assert response.status_code == 422

    def test_create_investor_invalid_sector(self, client):
        """Test that invalid sector values are rejected."""
        invalid_data = {
            "fund_name": "Invalid Fund",
            "ticket_size_min": 500000.0,
            "ticket_size_max": 10000000.0,
            "instruments": ["Equity"],
            "country_focus": ["Kenya"],
            "sector_focus": ["InvalidSector"]
        }
        response = client.post("/investors/", json=invalid_data)
        assert response.status_code == 422

    def test_create_investor_multiple_instruments(self, client):
        """Test creating investor with multiple instruments."""
        data = {
            "fund_name": "Multi Instrument Fund",
            "ticket_size_min": 1000000.0,
            "ticket_size_max": 50000000.0,
            "instruments": ["Equity", "Debt", "Mezzanine"],
            "country_focus": ["Nigeria", "Kenya"],
            "sector_focus": ["Energy", "Transport", "Water"]
        }
        response = client.post("/investors/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert len(result["instruments"]) == 3
        assert len(result["sector_focus"]) == 3


class TestGetInvestor:
    """Tests for investor retrieval endpoint."""

    def test_get_investor_success(self, client, sample_investor_data):
        """Test successful investor retrieval."""
        # Create investor first
        create_response = client.post("/investors/", json=sample_investor_data)
        investor_id = create_response.json()["id"]

        # Retrieve investor
        response = client.get(f"/investors/{investor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == investor_id
        assert data["fund_name"] == sample_investor_data["fund_name"]

    def test_get_investor_not_found(self, client):
        """Test retrieving non-existent investor returns 404."""
        response = client.get("/investors/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_investor_invalid_id(self, client):
        """Test retrieving with invalid ID format."""
        response = client.get("/investors/invalid")
        assert response.status_code == 422  # Validation error


class TestInvestorDataIntegrity:
    """Tests for investor data integrity and edge cases."""

    def test_investor_ticket_size_range(self, client):
        """Test investor with valid ticket size range."""
        data = {
            "fund_name": "Range Test Fund",
            "ticket_size_min": 100000.0,
            "ticket_size_max": 100000000.0,
            "instruments": ["Equity"],
            "country_focus": ["Kenya"],
            "sector_focus": ["Energy"]
        }
        response = client.post("/investors/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["ticket_size_min"] == 100000.0
        assert result["ticket_size_max"] == 100000000.0

    def test_investor_with_esg_constraints(self, client):
        """Test investor with ESG constraints."""
        data = {
            "fund_name": "ESG Fund",
            "ticket_size_min": 1000000.0,
            "ticket_size_max": 50000000.0,
            "instruments": ["Equity"],
            "country_focus": ["Nigeria"],
            "sector_focus": ["Energy"],
            "esg_constraints": "No fossil fuels, minimum 30% women in management"
        }
        response = client.post("/investors/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["esg_constraints"] == data["esg_constraints"]

    def test_investor_with_target_irr(self, client):
        """Test investor with target IRR."""
        data = {
            "fund_name": "High Return Fund",
            "ticket_size_min": 5000000.0,
            "ticket_size_max": 100000000.0,
            "instruments": ["Equity", "Mezzanine"],
            "target_irr": 25.5,
            "country_focus": ["South Africa"],
            "sector_focus": ["Mining"]
        }
        response = client.post("/investors/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["target_irr"] == 25.5

    def test_multiple_investors_independent(self, client, sample_investor_data):
        """Test that multiple investors are stored independently."""
        # Create first investor
        response1 = client.post("/investors/", json=sample_investor_data)
        id1 = response1.json()["id"]

        # Create second investor with different name
        modified_data = sample_investor_data.copy()
        modified_data["fund_name"] = "Different Fund"
        response2 = client.post("/investors/", json=modified_data)
        id2 = response2.json()["id"]

        # Verify they are different
        assert id1 != id2

        # Verify both can be retrieved
        get1 = client.get(f"/investors/{id1}")
        get2 = client.get(f"/investors/{id2}")

        assert get1.json()["fund_name"] == sample_investor_data["fund_name"]
        assert get2.json()["fund_name"] == "Different Fund"
