# tests/test_integration.py
"""
Integration tests for end-to-end workflows.
These tests verify that multiple components work together correctly.
"""
import pytest
from datetime import date, timedelta


class TestProjectInvestorIntroductionWorkflow:
    """
    Test the complete workflow:
    Project creation -> Investor creation -> Introduction -> NDA -> Approval
    """

    def test_complete_introduction_workflow(self, client, sample_investor_data, db_session):
        """Test the full introduction workflow from project to approval."""
        # Step 1: Create a project
        from backend.models import Project, Sector, ProjectStage
        project = Project(
            name="Lagos Solar Farm",
            sector=Sector.ENERGY,
            country="Nigeria",
            region="Lagos",
            stage=ProjectStage.FEASIBILITY,
            estimated_capex=50000000.0,
            funding_gap=30000000.0,
            revenue_model="Power Purchase Agreement with Nigerian government"
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # Verify project exists via API
        project_response = client.get(f"/projects/{project_id}")
        assert project_response.status_code == 200
        assert project_response.json()["name"] == "Lagos Solar Farm"

        # Step 2: Create an investor
        investor_response = client.post("/investors/", json=sample_investor_data)
        assert investor_response.status_code == 200
        investor_id = investor_response.json()["id"]

        # Step 3: Create an introduction
        introduction_data = {
            "investor_id": investor_id,
            "project_id": project_id,
            "message": "We are interested in investing in this solar project",
            "nda_executed": False,
            "sponsor_approved": False,
            "status": "Pending"
        }
        intro_response = client.post("/introductions/", json=introduction_data)
        assert intro_response.status_code == 200
        intro_id = intro_response.json()["id"]

        # Verify introduction was created
        get_intro = client.get(f"/introductions/{intro_id}")
        assert get_intro.status_code == 200
        assert get_intro.json()["status"] == "Pending"


class TestProjectVerificationWorkflow:
    """
    Test the verification workflow:
    Project -> V0 -> V1 -> V2 -> V3 (with bankability scores)
    """

    def test_verification_progression(self, client, db_session):
        """Test progressing a project through all verification levels."""
        from backend.models import Project, Sector, ProjectStage

        # Create project
        project = Project(
            name="Kenya Wind Farm",
            sector=Sector.ENERGY,
            country="Kenya",
            stage=ProjectStage.CONCEPT,
            estimated_capex=120000000.0,
            revenue_model="PPA"
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # V0: Submitted
        v0_response = client.post("/verifications/", json={
            "project_id": project_id,
            "level": "V0: Submitted"
        })
        assert v0_response.status_code == 200

        # V1: Sponsor Identity Verified
        v1_response = client.post("/verifications/", json={
            "project_id": project_id,
            "level": "V1: Sponsor Identity Verified"
        })
        assert v1_response.status_code == 200

        # V2: Documents Verified
        v2_response = client.post("/verifications/", json={
            "project_id": project_id,
            "level": "V2: Documents Verified"
        })
        assert v2_response.status_code == 200

        # V3: Bankability Screened (with scores)
        v3_response = client.post("/verifications/", json={
            "project_id": project_id,
            "level": "V3: Bankability Screened",
            "bankability": {
                "technical_readiness": 88,
                "financial_robustness": 75,
                "legal_clarity": 92,
                "esg_compliance": 85,
                "overall_score": 85.0,
                "risk_flags": ["Currency volatility"],
                "last_verified": str(date.today())
            }
        })
        assert v3_response.status_code == 200

        # Verify all verifications exist
        all_verifications = client.get(f"/verifications/project/{project_id}")
        assert all_verifications.status_code == 200
        assert len(all_verifications.json()) == 4

        # Verify latest is V3
        latest = client.get(f"/verifications/project/{project_id}/latest")
        assert latest.status_code == 200
        assert latest.json()["level"] == "V3: Bankability Screened"


class TestProjectDataRoomWorkflow:
    """
    Test the data room workflow:
    Project -> Create Data Room -> Add Documents -> Grant Access
    """

    def test_data_room_setup(self, client, db_session):
        """Test setting up a data room for a project."""
        from backend.models import Project, Sector, ProjectStage

        # Create project
        project = Project(
            name="Ghana Port Expansion",
            sector=Sector.PORTS,
            country="Ghana",
            stage=ProjectStage.PROCUREMENT,
            estimated_capex=500000000.0,
            revenue_model="Port fees"
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # Create data room with NDA requirement
        data_room_response = client.post("/data-rooms/", json={
            "project_id": project_id,
            "nda_required": True,
            "access_users": [101, 102, 103],
            "documents": {
                "executive_summary": "s3://aip-docs/ghana-port/exec-summary.pdf",
                "feasibility_study": "s3://aip-docs/ghana-port/feasibility.pdf",
                "financial_model": "s3://aip-docs/ghana-port/model.xlsx",
                "environmental_impact": "s3://aip-docs/ghana-port/eia.pdf"
            }
        })
        assert data_room_response.status_code == 200
        room_id = data_room_response.json()["id"]

        # Retrieve and verify data room
        get_room = client.get(f"/data-rooms/{room_id}")
        assert get_room.status_code == 200
        room_data = get_room.json()
        assert room_data["project_id"] == project_id
        assert room_data["nda_required"] == True


class TestEventProjectAssociation:
    """
    Test events with associated projects.
    """

    def test_event_with_multiple_projects(self, client, db_session):
        """Test creating an event that involves multiple projects."""
        from backend.models import Project, Sector, ProjectStage

        # Create multiple projects
        project_ids = []
        for i in range(3):
            project = Project(
                name=f"Event Project {i}",
                sector=Sector.ENERGY,
                country="South Africa",
                stage=ProjectStage.FEASIBILITY,
                estimated_capex=10000000.0 * (i + 1),
                revenue_model="PPA"
            )
            db_session.add(project)
            db_session.commit()
            project_ids.append(project.id)

        # Create event involving all projects
        event_response = client.post("/events/", json={
            "name": "South Africa Energy Summit",
            "description": "Showcase of energy projects in South Africa",
            "event_date": str(date.today() + timedelta(days=60)),
            "type": "Forum",
            "projects_involved": project_ids
        })
        assert event_response.status_code == 200
        event_data = event_response.json()
        assert event_data["name"] == "South Africa Energy Summit"


class TestAnalyticsWithProjectData:
    """
    Test analytics reports that reference project data.
    """

    def test_sector_report_with_projects(self, client, db_session):
        """Test creating an analytics report after creating sector projects."""
        from backend.models import Project, Sector, ProjectStage

        # Create projects in the energy sector
        for i in range(5):
            project = Project(
                name=f"Energy Project {i}",
                sector=Sector.ENERGY,
                country="Nigeria",
                stage=ProjectStage.FEASIBILITY,
                estimated_capex=20000000.0 * (i + 1),
                revenue_model="PPA"
            )
            db_session.add(project)
        db_session.commit()

        # Create sector analysis report
        report_response = client.post("/analytics/", json={
            "title": "Nigeria Energy Sector Q4 Analysis",
            "sector": "Energy",
            "country": "Nigeria",
            "content": """
                Nigeria Energy Sector Analysis
                ==============================

                Key Findings:
                - 5 active projects in pipeline
                - Total estimated capex: $300M
                - All projects at feasibility stage

                Recommendations:
                - Accelerate permitting process
                - Strengthen grid infrastructure
                - Attract more DFI participation
            """
        })
        assert report_response.status_code == 200
        assert report_response.json()["sector"] == "Energy"
        assert report_response.json()["country"] == "Nigeria"


class TestFullPlatformWorkflow:
    """
    Test a complete platform workflow simulating real usage.
    """

    def test_complete_deal_flow(self, client, sample_investor_data, db_session):
        """
        Simulate a complete deal flow:
        1. Sponsor submits project
        2. Project gets verified
        3. Investor registers
        4. Introduction is made
        5. Data room is created
        6. Event is scheduled
        7. Analytics report is generated
        """
        from backend.models import Project, Sector, ProjectStage

        # 1. Sponsor submits project
        project = Project(
            name="Tanzania Rail Corridor",
            sector=Sector.RAIL,
            country="Tanzania",
            stage=ProjectStage.CONCEPT,
            estimated_capex=2000000000.0,
            funding_gap=1500000000.0,
            revenue_model="Rail freight and passenger revenue"
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # 2. Project gets verified through levels
        for level in ["V0: Submitted", "V1: Sponsor Identity Verified"]:
            verify_response = client.post("/verifications/", json={
                "project_id": project_id,
                "level": level
            })
            assert verify_response.status_code == 200

        # 3. Investor registers
        investor_response = client.post("/investors/", json=sample_investor_data)
        assert investor_response.status_code == 200
        investor_id = investor_response.json()["id"]

        # 4. Introduction is made
        intro_response = client.post("/introductions/", json={
            "investor_id": investor_id,
            "project_id": project_id,
            "message": "Interested in the rail corridor project",
            "status": "Pending"
        })
        assert intro_response.status_code == 200

        # 5. Data room is created
        room_response = client.post("/data-rooms/", json={
            "project_id": project_id,
            "nda_required": True,
            "access_users": [investor_id],
            "documents": {
                "pre_feasibility": "s3://docs/tanzania-rail/prefeas.pdf"
            }
        })
        assert room_response.status_code == 200

        # 6. Event is scheduled
        event_response = client.post("/events/", json={
            "name": "Tanzania Rail Project Presentation",
            "description": "Investor presentation for Tanzania Rail Corridor",
            "event_date": str(date.today() + timedelta(days=14)),
            "type": "Presentation",
            "projects_involved": [project_id]
        })
        assert event_response.status_code == 200

        # 7. Analytics report is generated
        report_response = client.post("/analytics/", json={
            "title": "Tanzania Rail Investment Opportunity",
            "sector": "Rail",
            "country": "Tanzania",
            "content": "Analysis of the Tanzania Rail Corridor investment opportunity..."
        })
        assert report_response.status_code == 200

        # Verify complete flow succeeded
        assert client.get(f"/projects/{project_id}").status_code == 200
        assert client.get(f"/investors/{investor_id}").status_code == 200
        assert len(client.get(f"/verifications/project/{project_id}").json()) == 2


class TestConcurrentOperations:
    """
    Test multiple concurrent operations on the system.
    """

    def test_multiple_investors_same_project(self, client, db_session):
        """Test multiple investors expressing interest in the same project."""
        from backend.models import Project, Sector, ProjectStage

        # Create project
        project = Project(
            name="Popular Mining Project",
            sector=Sector.MINING,
            country="Zambia",
            stage=ProjectStage.PROCUREMENT,
            estimated_capex=300000000.0,
            revenue_model="Copper sales"
        )
        db_session.add(project)
        db_session.commit()
        project_id = project.id

        # Create multiple investors and introductions
        for i in range(5):
            investor_response = client.post("/investors/", json={
                "fund_name": f"Fund {i}",
                "ticket_size_min": 1000000.0,
                "ticket_size_max": 50000000.0,
                "instruments": ["Equity"],
                "country_focus": ["Zambia"],
                "sector_focus": ["Mining"]
            })
            investor_id = investor_response.json()["id"]

            intro_response = client.post("/introductions/", json={
                "investor_id": investor_id,
                "project_id": project_id,
                "message": f"Interest from Fund {i}",
                "status": "Pending"
            })
            assert intro_response.status_code == 200

    def test_multiple_projects_same_investor(self, client, sample_investor_data, db_session):
        """Test one investor interested in multiple projects."""
        from backend.models import Project, Sector, ProjectStage

        # Create investor
        investor_response = client.post("/investors/", json=sample_investor_data)
        investor_id = investor_response.json()["id"]

        # Create multiple projects and introductions
        for i in range(3):
            project = Project(
                name=f"Multi-Interest Project {i}",
                sector=Sector.ENERGY,
                country="Kenya",
                stage=ProjectStage.FEASIBILITY,
                estimated_capex=15000000.0 * (i + 1),
                revenue_model="PPA"
            )
            db_session.add(project)
            db_session.commit()

            intro_response = client.post("/introductions/", json={
                "investor_id": investor_id,
                "project_id": project.id,
                "message": f"Interest in project {i}",
                "status": "Pending"
            })
            assert intro_response.status_code == 200
