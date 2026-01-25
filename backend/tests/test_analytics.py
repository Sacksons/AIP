# tests/test_analytics.py
import pytest


class TestCreateAnalyticReport:
    """Tests for analytic report creation endpoint."""

    def test_create_report_success(self, client):
        """Test successful report creation."""
        report_data = {
            "title": "Q4 2024 Infrastructure Investment Report",
            "sector": "Energy",
            "country": "Nigeria",
            "content": "Detailed analysis of energy sector investments in Nigeria..."
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == report_data["title"]
        assert data["sector"] == "Energy"
        assert "id" in data
        assert "created_at" in data

    def test_create_report_minimal_data(self, client):
        """Test creating report with only required fields."""
        report_data = {
            "title": "Basic Report",
            "content": "Report content here"
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Basic Report"
        assert data["sector"] is None
        assert data["country"] is None

    def test_create_report_all_sectors(self, client):
        """Test creating reports for all sectors."""
        sectors = ["Energy", "Mining", "Water", "Transport", "Ports", "Rail", "Roads", "Agriculture", "Health"]
        for sector in sectors:
            report_data = {
                "title": f"{sector} Sector Analysis",
                "sector": sector,
                "content": f"Comprehensive analysis of the {sector.lower()} sector..."
            }
            response = client.post("/analytics/", json=report_data)
            assert response.status_code == 200
            assert response.json()["sector"] == sector

    def test_create_report_with_country(self, client):
        """Test creating country-specific report."""
        report_data = {
            "title": "Kenya Infrastructure Overview",
            "country": "Kenya",
            "content": "Analysis of Kenya's infrastructure development..."
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        assert response.json()["country"] == "Kenya"

    def test_create_report_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        incomplete_data = {"title": "Incomplete Report"}
        response = client.post("/analytics/", json=incomplete_data)
        assert response.status_code == 422

    def test_create_report_long_content(self, client):
        """Test creating report with long content."""
        long_content = "A" * 10000  # 10,000 characters
        report_data = {
            "title": "Long Content Report",
            "content": long_content
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        assert len(response.json()["content"]) == 10000


class TestGetAnalyticReport:
    """Tests for analytic report retrieval endpoint."""

    def test_get_report_success(self, client):
        """Test successful report retrieval."""
        # Create report
        report_data = {
            "title": "Retrievable Report",
            "sector": "Mining",
            "country": "South Africa",
            "content": "Mining sector analysis for South Africa"
        }
        create_response = client.post("/analytics/", json=report_data)
        report_id = create_response.json()["id"]

        # Retrieve report
        response = client.get(f"/analytics/{report_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
        assert data["title"] == "Retrievable Report"
        assert data["sector"] == "Mining"

    def test_get_report_not_found(self, client):
        """Test retrieving non-existent report returns 404."""
        response = client.get("/analytics/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_report_invalid_id(self, client):
        """Test retrieving with invalid ID format."""
        response = client.get("/analytics/invalid")
        assert response.status_code == 422


class TestReportContent:
    """Tests for report content variations."""

    def test_report_with_markdown_content(self, client):
        """Test report with markdown-formatted content."""
        content = """
# Executive Summary

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Recommendations
1. First recommendation
2. Second recommendation

### Detailed Analysis
Lorem ipsum dolor sit amet...
        """
        report_data = {
            "title": "Markdown Report",
            "content": content
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        assert "# Executive Summary" in response.json()["content"]

    def test_report_with_special_characters(self, client):
        """Test report with special characters."""
        content = "Revenue: $1.5M | Growth: 15% | Countries: Nigeria & Kenya"
        report_data = {
            "title": "Special Chars Report",
            "content": content
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        assert "$1.5M" in response.json()["content"]

    def test_report_with_unicode(self, client):
        """Test report with unicode characters."""
        content = "African Union: Aфрика - アフリカ - 非洲"
        report_data = {
            "title": "Unicode Report",
            "content": content
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200


class TestReportTypes:
    """Tests for different report use cases."""

    def test_sector_analysis_report(self, client):
        """Test creating a sector analysis report."""
        report_data = {
            "title": "Energy Sector Deep Dive",
            "sector": "Energy",
            "content": """
                Energy sector analysis covering:
                - Solar installations
                - Wind farms
                - Hydroelectric projects
                - Grid infrastructure
            """
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200

    def test_country_overview_report(self, client):
        """Test creating a country overview report."""
        report_data = {
            "title": "Ethiopia Country Profile",
            "country": "Ethiopia",
            "content": """
                Country investment profile:
                - GDP growth trends
                - Infrastructure gaps
                - Key opportunities
                - Risk factors
            """
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200

    def test_cross_sector_report(self, client):
        """Test creating a cross-sector regional report."""
        report_data = {
            "title": "West Africa Infrastructure Index",
            "content": """
                Regional infrastructure index covering:
                - Nigeria
                - Ghana
                - Senegal
                - Côte d'Ivoire

                Sectors covered:
                - Energy
                - Transport
                - Ports
            """
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200


class TestReportDataIntegrity:
    """Tests for report data integrity."""

    def test_multiple_reports_independent(self, client):
        """Test that multiple reports are stored independently."""
        # Create first report
        response1 = client.post("/analytics/", json={
            "title": "Report One",
            "content": "Content one"
        })
        id1 = response1.json()["id"]

        # Create second report
        response2 = client.post("/analytics/", json={
            "title": "Report Two",
            "content": "Content two"
        })
        id2 = response2.json()["id"]

        # Verify they are different
        assert id1 != id2

        # Verify both can be retrieved correctly
        get1 = client.get(f"/analytics/{id1}")
        get2 = client.get(f"/analytics/{id2}")

        assert get1.json()["title"] == "Report One"
        assert get2.json()["title"] == "Report Two"

    def test_report_timestamp(self, client):
        """Test that reports have creation timestamps."""
        report_data = {
            "title": "Timestamped Report",
            "content": "Content with timestamp"
        }
        response = client.post("/analytics/", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None
