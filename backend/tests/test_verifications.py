# tests/test_verifications.py
import pytest
from datetime import date


class TestVerificationPing:
    """Tests for verification service health check."""

    def test_ping_endpoint(self, client):
        """Test the ping endpoint returns ok."""
        response = client.get("/verifications/ping")
        assert response.status_code == 200
        assert response.json() == {"ok": True}


class TestCreateVerification:
    """Tests for verification creation endpoint."""

    def test_create_verification_v0(self, client, db_session):
        """Test creating a V0 (Submitted) verification."""
        # Create a project first
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Verification Test Project",
            sector=Sector.ENERGY,
            country="Nigeria",
            stage=ProjectStage.CONCEPT,
            estimated_capex=10000000.0,
            revenue_model="PPA"
        )
        db_session.add(project)
        db_session.commit()

        # Create verification
        verification_data = {
            "project_id": project.id,
            "level": "V0: Submitted"
        }
        response = client.post("/verifications/", json=verification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project.id
        assert data["level"] == "V0: Submitted"

    def test_create_verification_with_bankability_score(self, client, db_session):
        """Test creating verification with full bankability scoring."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Bankability Test Project",
            sector=Sector.TRANSPORT,
            country="Kenya",
            stage=ProjectStage.FEASIBILITY,
            estimated_capex=50000000.0,
            revenue_model="Toll collection"
        )
        db_session.add(project)
        db_session.commit()

        verification_data = {
            "project_id": project.id,
            "level": "V3: Bankability Screened",
            "bankability": {
                "technical_readiness": 85,
                "financial_robustness": 78,
                "legal_clarity": 90,
                "esg_compliance": 82,
                "overall_score": 83.75,
                "risk_flags": ["Currency risk", "Political uncertainty"],
                "last_verified": str(date.today())
            }
        }
        response = client.post("/verifications/", json=verification_data)
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "V3: Bankability Screened"

    def test_create_verification_project_not_found(self, client):
        """Test creating verification for non-existent project fails."""
        verification_data = {
            "project_id": 99999,
            "level": "V0: Submitted"
        }
        response = client.post("/verifications/", json=verification_data)
        assert response.status_code == 404
        assert "project not found" in response.json()["detail"].lower()

    def test_create_verification_invalid_level(self, client, db_session):
        """Test creating verification with invalid level fails."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Invalid Level Project",
            sector=Sector.WATER,
            country="Ghana",
            stage=ProjectStage.CONCEPT,
            estimated_capex=5000000.0,
            revenue_model="Government contract"
        )
        db_session.add(project)
        db_session.commit()

        verification_data = {
            "project_id": project.id,
            "level": "Invalid Level"
        }
        response = client.post("/verifications/", json=verification_data)
        assert response.status_code == 422


class TestGetVerification:
    """Tests for verification retrieval endpoint."""

    def test_get_verification_success(self, client, db_session):
        """Test successful verification retrieval."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Get Verification Project",
            sector=Sector.MINING,
            country="Zambia",
            stage=ProjectStage.PROCUREMENT,
            estimated_capex=100000000.0,
            revenue_model="Commodity sales"
        )
        db_session.add(project)
        db_session.commit()

        # Create verification
        verification_data = {
            "project_id": project.id,
            "level": "V1: Sponsor Identity Verified"
        }
        create_response = client.post("/verifications/", json=verification_data)
        verification_id = create_response.json()["id"]

        # Retrieve verification
        response = client.get(f"/verifications/{verification_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == verification_id
        assert data["level"] == "V1: Sponsor Identity Verified"

    def test_get_verification_not_found(self, client):
        """Test retrieving non-existent verification returns 404."""
        response = client.get("/verifications/99999")
        assert response.status_code == 404


class TestVerificationByProject:
    """Tests for verification queries by project."""

    def test_list_verifications_by_project(self, client, db_session):
        """Test listing all verifications for a project."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Multi Verification Project",
            sector=Sector.AGRICULTURE,
            country="Ethiopia",
            stage=ProjectStage.FEASIBILITY,
            estimated_capex=20000000.0,
            revenue_model="Crop sales"
        )
        db_session.add(project)
        db_session.commit()

        # Create multiple verifications
        levels = ["V0: Submitted", "V1: Sponsor Identity Verified", "V2: Documents Verified"]
        for level in levels:
            client.post("/verifications/", json={
                "project_id": project.id,
                "level": level
            })

        # List verifications
        response = client.get(f"/verifications/project/{project.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_verifications_project_not_found(self, client):
        """Test listing verifications for non-existent project."""
        response = client.get("/verifications/project/99999")
        assert response.status_code == 404

    def test_get_latest_verification(self, client, db_session):
        """Test getting the latest verification for a project."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Latest Verification Project",
            sector=Sector.HEALTH,
            country="Rwanda",
            stage=ProjectStage.CONSTRUCTION,
            estimated_capex=15000000.0,
            revenue_model="Healthcare services"
        )
        db_session.add(project)
        db_session.commit()

        # Create verifications in order
        levels = ["V0: Submitted", "V1: Sponsor Identity Verified", "V2: Documents Verified"]
        for level in levels:
            client.post("/verifications/", json={
                "project_id": project.id,
                "level": level
            })

        # Get latest
        response = client.get(f"/verifications/project/{project.id}/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "V2: Documents Verified"

    def test_get_latest_verification_no_verifications(self, client, db_session):
        """Test getting latest verification when none exist."""
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="No Verification Project",
            sector=Sector.PORTS,
            country="Tanzania",
            stage=ProjectStage.CONCEPT,
            estimated_capex=200000000.0,
            revenue_model="Port fees"
        )
        db_session.add(project)
        db_session.commit()

        response = client.get(f"/verifications/project/{project.id}/latest")
        assert response.status_code == 404


class TestVerificationLevels:
    """Tests for all verification levels."""

    def test_all_verification_levels(self, client, db_session):
        """Test creating verifications at all levels."""
        from backend.models import Project, Sector, ProjectStage
        levels = [
            "V0: Submitted",
            "V1: Sponsor Identity Verified",
            "V2: Documents Verified",
            "V3: Bankability Screened"
        ]

        for i, level in enumerate(levels):
            project = Project(
                name=f"Level {i} Project",
                sector=Sector.RAIL,
                country="South Africa",
                stage=ProjectStage.OPERATION,
                estimated_capex=500000000.0,
                revenue_model="Rail freight"
            )
            db_session.add(project)
            db_session.commit()

            response = client.post("/verifications/", json={
                "project_id": project.id,
                "level": level
            })
            assert response.status_code == 200
            assert response.json()["level"] == level
