# tests/test_projects.py
import pytest
from backend.models import Sector, ProjectStage


class TestCreateProject:
    """Tests for project creation endpoint."""

    def test_create_project_success(self, client, sample_project_data):
        """Test successful project creation."""
        response = client.post("/projects/", json=sample_project_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["country"] == sample_project_data["country"]
        assert "id" in data

    def test_create_project_minimal_data(self, client):
        """Test creating project with only required fields."""
        minimal_data = {
            "name": "Minimal Project",
            "sector": "Energy",
            "country": "Kenya",
            "stage": "Concept",
            "estimated_capex": 1000000.0,
            "revenue_model": "PPA"
        }
        response = client.post("/projects/", json=minimal_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["funding_gap"] is None

    def test_create_project_with_all_fields(self, client):
        """Test creating project with all optional fields."""
        full_data = {
            "name": "Full Project",
            "sector": "Transport",
            "country": "Nigeria",
            "region": "Lagos",
            "gps_location": "6.5244,3.3792",
            "stage": "Feasibility",
            "estimated_capex": 100000000.0,
            "funding_gap": 50000000.0,
            "revenue_model": "Toll collection",
            "offtaker": "Government of Nigeria",
            "tariff_mechanism": "Inflation-indexed",
            "concession_length": 30,
            "fx_exposure": "USD/NGN",
            "political_risk_mitigation": "MIGA guarantee",
            "sovereign_support": "Government letter of support",
            "technology": "Highway construction",
            "epc_status": "Tendering",
            "land_acquisition_status": "In progress",
            "esg_category": "Category B",
            "permits_status": "Pending environmental approval"
        }
        response = client.post("/projects/", json=full_data)
        assert response.status_code == 200
        data = response.json()
        assert data["concession_length"] == 30
        assert data["region"] == "Lagos"

    def test_create_project_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        incomplete_data = {"name": "Incomplete Project"}
        response = client.post("/projects/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_project_invalid_sector(self, client):
        """Test that invalid sector values are rejected."""
        invalid_data = {
            "name": "Invalid Sector Project",
            "sector": "InvalidSector",
            "country": "Kenya",
            "stage": "Concept",
            "estimated_capex": 1000000.0,
            "revenue_model": "PPA"
        }
        response = client.post("/projects/", json=invalid_data)
        assert response.status_code == 422

    def test_create_project_invalid_stage(self, client):
        """Test that invalid stage values are rejected."""
        invalid_data = {
            "name": "Invalid Stage Project",
            "sector": "Energy",
            "country": "Kenya",
            "stage": "InvalidStage",
            "estimated_capex": 1000000.0,
            "revenue_model": "PPA"
        }
        response = client.post("/projects/", json=invalid_data)
        assert response.status_code == 422


class TestGetProject:
    """Tests for project retrieval endpoint."""

    def test_get_project_success(self, client, sample_project_data):
        """Test successful project retrieval."""
        # Create project
        create_response = client.post("/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]

        # Retrieve project
        response = client.get(f"/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == sample_project_data["name"]

    def test_get_project_not_found(self, client):
        """Test retrieving non-existent project returns 404."""
        response = client.get("/projects/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_project_invalid_id(self, client):
        """Test retrieving with invalid ID format."""
        response = client.get("/projects/invalid")
        assert response.status_code == 422


class TestListProjects:
    """Tests for project listing endpoint."""

    def test_list_projects_empty(self, client):
        """Test listing projects when none exist."""
        response = client.get("/projects/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_projects_multiple(self, client, sample_project_data):
        """Test listing multiple projects."""
        # Create multiple projects
        for i in range(3):
            data = sample_project_data.copy()
            data["name"] = f"Project {i}"
            client.post("/projects/", json=data)

        response = client.get("/projects/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_projects_with_pagination(self, client, sample_project_data):
        """Test listing projects with pagination."""
        # Create 5 projects
        for i in range(5):
            data = sample_project_data.copy()
            data["name"] = f"Project {i}"
            client.post("/projects/", json=data)

        # Get first 2
        response = client.get("/projects/?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Get next 2
        response = client.get("/projects/?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_projects_filter_by_country(self, client):
        """Test filtering projects by country."""
        # Create projects in different countries
        countries = ["Nigeria", "Kenya", "Nigeria"]
        for i, country in enumerate(countries):
            data = {
                "name": f"Project {i}",
                "sector": "Energy",
                "country": country,
                "stage": "Concept",
                "estimated_capex": 1000000.0,
                "revenue_model": "PPA"
            }
            client.post("/projects/", json=data)

        # Filter by Nigeria
        response = client.get("/projects/?country=Nigeria")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 2
        for p in projects:
            assert p["country"] == "Nigeria"


class TestProjectDataIntegrity:
    """Tests for project data integrity."""

    def test_project_capex_values(self, client):
        """Test project with various capex values."""
        data = {
            "name": "Large Capex Project",
            "sector": "Mining",
            "country": "South Africa",
            "stage": "Construction",
            "estimated_capex": 5000000000.0,  # 5 billion
            "funding_gap": 2000000000.0,
            "revenue_model": "Commodity sales"
        }
        response = client.post("/projects/", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["estimated_capex"] == 5000000000.0
        assert result["funding_gap"] == 2000000000.0

    def test_project_all_stages(self, client):
        """Test creating projects in all stages."""
        stages = ["Concept", "Feasibility", "Procurement", "Construction", "Operation"]
        for stage in stages:
            data = {
                "name": f"{stage} Stage Project",
                "sector": "Water",
                "country": "Ethiopia",
                "stage": stage,
                "estimated_capex": 10000000.0,
                "revenue_model": "Government contract"
            }
            response = client.post("/projects/", json=data)
            assert response.status_code == 200
            assert response.json()["stage"] == stage

    def test_project_all_sectors(self, client):
        """Test creating projects in all sectors."""
        sectors = ["Energy", "Mining", "Water", "Transport", "Ports", "Rail", "Roads", "Agriculture", "Health"]
        for sector in sectors:
            data = {
                "name": f"{sector} Project",
                "sector": sector,
                "country": "Ghana",
                "stage": "Concept",
                "estimated_capex": 5000000.0,
                "revenue_model": "PPA"
            }
            response = client.post("/projects/", json=data)
            assert response.status_code == 200
            assert response.json()["sector"] == sector
