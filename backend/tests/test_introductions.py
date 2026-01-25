# tests/test_introductions.py
import pytest


class TestCreateIntroduction:
    """Tests for introduction creation endpoint."""

    def test_create_introduction_success(self, client, sample_investor_data, sample_project_data, db_session):
        """Test successful introduction creation."""
        # First create an investor
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        # Create a project directly in db (since projects endpoint may not exist)
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name=sample_project_data["name"],
            sector=Sector.ENERGY,
            country=sample_project_data["country"],
            stage=ProjectStage.FEASIBILITY,
            estimated_capex=sample_project_data["estimated_capex"],
            revenue_model=sample_project_data["revenue_model"]
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # Create introduction
        intro_data = {
            "investor_id": investor_id,
            "project_id": project_id,
            "message": "Interested in this project",
            "nda_executed": False,
            "sponsor_approved": False,
            "status": "Pending"
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        data = response.json()
        assert data["investor_id"] == investor_id
        assert data["project_id"] == project_id
        assert data["status"] == "Pending"

    def test_create_introduction_minimal_data(self, client, sample_investor_data, db_session):
        """Test creating introduction with only required fields."""
        # Create investor
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        # Create project in db
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Test Project",
            sector=Sector.ENERGY,
            country="Kenya",
            stage=ProjectStage.CONCEPT,
            estimated_capex=10000000.0,
            revenue_model="PPA"
        )
        db_session.add(project)
        db_session.commit()

        # Create introduction with minimal data
        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        data = response.json()
        assert data["nda_executed"] == False
        assert data["sponsor_approved"] == False
        assert data["status"] == "Pending"

    def test_create_introduction_missing_investor_id(self, client):
        """Test that missing investor_id is rejected."""
        intro_data = {
            "project_id": 1,
            "message": "Test message"
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 422


class TestGetIntroduction:
    """Tests for introduction retrieval endpoint."""

    def test_get_introduction_success(self, client, sample_investor_data, db_session):
        """Test successful introduction retrieval."""
        # Create investor
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        # Create project
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Test Project",
            sector=Sector.TRANSPORT,
            country="South Africa",
            stage=ProjectStage.PROCUREMENT,
            estimated_capex=75000000.0,
            revenue_model="Toll collection"
        )
        db_session.add(project)
        db_session.commit()

        # Create introduction
        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id,
            "message": "Looking to invest",
            "status": "Pending"
        }
        create_response = client.post("/introductions/", json=intro_data)
        intro_id = create_response.json()["id"]

        # Retrieve introduction
        response = client.get(f"/introductions/{intro_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == intro_id
        assert data["message"] == "Looking to invest"

    def test_get_introduction_not_found(self, client):
        """Test retrieving non-existent introduction returns 404."""
        response = client.get("/introductions/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestIntroductionWorkflow:
    """Tests for introduction workflow states."""

    def test_introduction_default_status(self, client, sample_investor_data, db_session):
        """Test that new introductions default to Pending status."""
        # Setup
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Default Status Project",
            sector=Sector.WATER,
            country="Ghana",
            stage=ProjectStage.CONSTRUCTION,
            estimated_capex=25000000.0,
            revenue_model="Government contract"
        )
        db_session.add(project)
        db_session.commit()

        # Create introduction without specifying status
        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        assert response.json()["status"] == "Pending"

    def test_introduction_nda_defaults_to_false(self, client, sample_investor_data, db_session):
        """Test that NDA executed defaults to False."""
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="NDA Test Project",
            sector=Sector.MINING,
            country="Zambia",
            stage=ProjectStage.OPERATION,
            estimated_capex=150000000.0,
            revenue_model="Commodity sales"
        )
        db_session.add(project)
        db_session.commit()

        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        assert response.json()["nda_executed"] == False

    def test_introduction_with_nda_executed(self, client, sample_investor_data, db_session):
        """Test creating introduction with NDA already executed."""
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="NDA Executed Project",
            sector=Sector.AGRICULTURE,
            country="Ethiopia",
            stage=ProjectStage.FEASIBILITY,
            estimated_capex=8000000.0,
            revenue_model="Crop sales"
        )
        db_session.add(project)
        db_session.commit()

        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id,
            "nda_executed": True,
            "status": "In Progress"
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        assert response.json()["nda_executed"] == True
        assert response.json()["status"] == "In Progress"


class TestIntroductionValidation:
    """Tests for introduction data validation."""

    def test_introduction_with_long_message(self, client, sample_investor_data, db_session):
        """Test introduction with a long message."""
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Long Message Project",
            sector=Sector.HEALTH,
            country="Rwanda",
            stage=ProjectStage.CONCEPT,
            estimated_capex=20000000.0,
            revenue_model="Healthcare services"
        )
        db_session.add(project)
        db_session.commit()

        long_message = "A" * 1000  # 1000 character message
        intro_data = {
            "investor_id": investor_id,
            "project_id": project.id,
            "message": long_message
        }
        response = client.post("/introductions/", json=intro_data)
        assert response.status_code == 200
        assert len(response.json()["message"]) == 1000
