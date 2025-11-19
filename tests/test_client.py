"""Tests for OpenCaselist API client"""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from opencaselist.client import (
    CaselistResource,
    CiteResource,
    OpenCaselistClient,
    RoundResource,
    SchoolResource,
    TeamResource,
)
from opencaselist.exceptions import APIError, AuthenticationError, NotFoundError
from opencaselist.models import (
    Caselist,
    Cite,
    Download,
    File,
    History,
    Recent,
    Round,
    School,
    SearchResult,
    TabroomChapter,
    TabroomLink,
    TabroomRound,
    TabroomStudent,
    Team,
)


@pytest.fixture
def mock_session():
    """Create a mock session for testing"""
    session = MagicMock(spec=requests.Session)
    return session


@pytest.fixture
def client(mock_session):
    """Create a client with mocked session"""
    with patch("opencaselist.client.requests.Session", return_value=mock_session):
        # Create client without auto-login
        client = OpenCaselistClient(auto_login=False)
        client._session = mock_session
        return client


class TestOpenCaselistClient:
    def test_login_success(self, mock_session):
        """Test successful login"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.post.return_value = mock_response

        with patch("opencaselist.client.requests.Session", return_value=mock_session):
            with patch("opencaselist.client.input", return_value="testuser"):
                with patch("opencaselist.client.getpass", return_value="testpass"):
                    client = OpenCaselistClient(auto_login=True)

        mock_session.post.assert_called_once()
        assert client._authenticated is True

    def test_login_failure(self, mock_session):
        """Test failed login"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_session.post.return_value = mock_response

        with patch("opencaselist.client.requests.Session", return_value=mock_session):
            client = OpenCaselistClient(auto_login=False)
            client._session = mock_session

            with pytest.raises(AuthenticationError):
                client.login(username="testuser", password="wrongpass")

    def test_caselists(self, client, mock_session):
        """Test fetching all caselists"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"slug": "hspolicy25", "name": "HS Policy 2025"},
            {"slug": "hsld25", "name": "HS LD 2025"},
        ]
        mock_session.get.return_value = mock_response

        caselists = client.caselists()

        assert len(caselists) == 2
        assert isinstance(caselists[0], Caselist)
        assert caselists[0].slug == "hspolicy25"
        assert caselists[1].slug == "hsld25"

    def test_search(self, client, mock_session):
        """Test search functionality"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "shard": "hspolicy25",
                "content": "debate content",
                "path": "/path",
            }
        ]
        mock_session.get.return_value = mock_response

        results = client.search("test query")

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].content == "debate content"
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[1]["params"]["q"] == "test query"

    def test_download(self, client, mock_session):
        """Test file download"""
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_session.get.return_value = mock_response

        content = client.download(file_id=123)

        assert content == b"file content"
        mock_session.get.assert_called_once()

    def test_tabroom_students(self, client, mock_session):
        """Test fetching Tabroom students"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "first": "John", "last": "Doe"},
            {"id": 2, "first": "Jane", "last": "Smith"},
        ]
        mock_session.get.return_value = mock_response

        students = client.tabroom_students()

        assert len(students) == 2
        assert isinstance(students[0], TabroomStudent)
        assert students[0].first == "John"
        assert students[1].last == "Smith"

    def test_tabroom_rounds(self, client, mock_session):
        """Test fetching Tabroom rounds"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "tournament": "TOC",
                "round": "Quarters",
                "side": "A",
                "opponent": "Westminster",
                "judge": "John Doe",
                "start_time": "2025-11-18T10:00:00Z",
                "share": "public",
            }
        ]
        mock_session.get.return_value = mock_response

        rounds = client.tabroom_rounds(slug="test-slug")

        assert len(rounds) == 1
        assert isinstance(rounds[0], TabroomRound)
        assert rounds[0].tournament == "TOC"
        assert rounds[0].round == "Quarters"

    def test_tabroom_chapters(self, client, mock_session):
        """Test fetching Tabroom chapters"""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1, "name": "NorthHollywood"}]
        mock_session.get.return_value = mock_response

        chapters = client.tabroom_chapters()

        assert len(chapters) == 1
        assert isinstance(chapters[0], TabroomChapter)
        assert chapters[0].name == "NorthHollywood"

    def test_create_tabroom_link(self, client, mock_session):
        """Test creating a Tabroom link"""
        mock_response = Mock()
        mock_response.json.return_value = {"slug": "NorthHollywood-BeLu"}
        mock_session.post.return_value = mock_response

        link = client.create_tabroom_link(slug="NorthHollywood-BeLu")

        assert isinstance(link, TabroomLink)
        assert link.slug == "NorthHollywood-BeLu"

    def test_openev_files(self, client, mock_session):
        """Test fetching OpenEv files"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "openev_id": 1,
                "title": "Debate Cards",
                "path": "/files/cards.docx",
                "year": "2025",
                "camp": "Michigan",
                "lab": "Lab 1",
                "tags": ["policy"],
                "file": "/upload/file.docx",
                "filename": "cards.docx",
            }
        ]
        mock_session.get.return_value = mock_response

        files = client.openev_files(year="2025")

        assert len(files) == 1
        assert isinstance(files[0], File)
        assert files[0].title == "Debate Cards"
        assert files[0].year == "2025"

    def test_create_openev_file(self, client, mock_session):
        """Test creating an OpenEv file"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "openev_id": 1,
            "title": "New Cards",
            "year": "2025",
        }
        mock_session.post.return_value = mock_response

        file = client.create_openev_file(title="New Cards", year="2025")

        assert isinstance(file, File)
        assert file.title == "New Cards"

    def test_delete_openev_file(self, client, mock_session):
        """Test deleting an OpenEv file"""
        mock_response = Mock()
        mock_session.delete.return_value = mock_response

        client.delete_openev_file(file_id=123)

        mock_session.delete.assert_called_once()
        assert "/openev/123" in mock_session.delete.call_args[0][0]


class TestCaselistResource:
    @pytest.fixture
    def caselist_resource(self, mock_session):
        return CaselistResource(mock_session, "hspolicy25")

    def test_get_caselist(self, caselist_resource, mock_session):
        """Test getting caselist details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "slug": "hspolicy25",
            "name": "HS Policy 2025",
        }
        mock_session.request.return_value = mock_response

        caselist = caselist_resource.get()

        assert isinstance(caselist, Caselist)
        assert caselist.slug == "hspolicy25"

    def test_schools(self, caselist_resource, mock_session):
        """Test getting schools in a caselist"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "NorthHollywood", "display_name": "Greenhill"}
        ]
        mock_session.request.return_value = mock_response

        schools = caselist_resource.schools()

        assert len(schools) == 1
        assert isinstance(schools[0], School)
        assert schools[0].name == "NorthHollywood"

    def test_create_school(self, caselist_resource, mock_session):
        """Test creating a school"""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "newschool", "state": "TX"}
        mock_session.request.return_value = mock_response

        school = caselist_resource.create_school(name="newschool", state="TX")

        assert isinstance(school, School)
        assert school.name == "newschool"

    def test_recent(self, caselist_resource, mock_session):
        """Test getting recent modifications"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "team_id": 1,
                "side": "A",
                "tournament": "TOC",
                "team_name": "BeLu",
                "school_name": "NorthHollywood",
                "updated_at": "2025-11-18T10:00:00Z",
            }
        ]
        mock_session.request.return_value = mock_response

        recent = caselist_resource.recent()

        assert len(recent) == 1
        assert isinstance(recent[0], Recent)
        assert recent[0].tournament == "TOC"

    def test_downloads(self, caselist_resource, mock_session):
        """Test getting bulk downloads"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "All Rounds", "url": "http://example.com"}
        ]
        mock_session.request.return_value = mock_response

        downloads = caselist_resource.downloads()

        assert len(downloads) == 1
        assert isinstance(downloads[0], Download)
        assert downloads[0].name == "All Rounds"


class TestSchoolResource:
    @pytest.fixture
    def school_resource(self, mock_session):
        return SchoolResource(mock_session, "hspolicy25", "NorthHollywood")

    def test_get_school(self, school_resource, mock_session):
        """Test getting school details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "NorthHollywood",
            "display_name": "Greenhill",
        }
        mock_session.request.return_value = mock_response

        school = school_resource.get()

        assert isinstance(school, School)
        assert school.name == "NorthHollywood"

    def test_teams(self, school_resource, mock_session):
        """Test getting teams in a school"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "BeLu", "display_name": "Johnson-Lee"}
        ]
        mock_session.request.return_value = mock_response

        teams = school_resource.teams()

        assert len(teams) == 1
        assert isinstance(teams[0], Team)
        assert teams[0].name == "BeLu"

    def test_create_team(self, school_resource, mock_session):
        """Test creating a team"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "ab",
            "display_name": "Anderson-Brown",
        }
        mock_session.request.return_value = mock_response

        team = school_resource.create_team(name="ab")

        assert isinstance(team, Team)
        assert team.name == "ab"

    def test_history(self, school_resource, mock_session):
        """Test getting school history"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "description": "Added team",
                "updated_by": "user@example.com",
                "updated_at": "2025-11-18T10:00:00Z",
            }
        ]
        mock_session.request.return_value = mock_response

        history = school_resource.history()

        assert len(history) == 1
        assert isinstance(history[0], History)
        assert history[0].description == "Added team"


class TestTeamResource:
    @pytest.fixture
    def team_resource(self, mock_session):
        return TeamResource(mock_session, "hspolicy25", "NorthHollywood", "BeLu")

    def test_get_team(self, team_resource, mock_session):
        """Test getting team details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "BeLu",
            "display_name": "Johnson-Lee",
        }
        mock_session.request.return_value = mock_response

        team = team_resource.get()

        assert isinstance(team, Team)
        assert team.name == "BeLu"

    def test_patch_team(self, team_resource, mock_session):
        """Test updating team details"""
        mock_response = Mock()
        mock_response.json.return_value = {"name": "BeLu", "notes": "Updated notes"}
        mock_session.request.return_value = mock_response

        team = team_resource.patch(notes="Updated notes")

        assert isinstance(team, Team)
        assert team.notes == "Updated notes"

    def test_delete_team(self, team_resource, mock_session):
        """Test deleting a team"""
        mock_response = Mock()
        mock_response.content = None
        mock_session.request.return_value = mock_response

        team_resource.delete()

        mock_session.request.assert_called_once()

    def test_rounds(self, team_resource, mock_session):
        """Test getting team rounds"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"tournament": "TOC", "side": "A", "opponent": "Westminster KN"}
        ]
        mock_session.request.return_value = mock_response

        rounds = team_resource.rounds()

        assert len(rounds) == 1
        assert isinstance(rounds[0], Round)
        assert rounds[0].tournament == "TOC"

    def test_rounds_with_side_filter(self, team_resource, mock_session):
        """Test getting team rounds filtered by side"""
        mock_response = Mock()
        mock_response.json.return_value = [{"tournament": "TOC", "side": "A"}]
        mock_session.request.return_value = mock_response

        rounds = team_resource.rounds(side="A")

        assert len(rounds) == 1
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["side"] == "A"

    def test_create_round(self, team_resource, mock_session):
        """Test creating a round"""
        mock_response = Mock()
        mock_response.json.return_value = {"tournament": "TOC", "side": "A"}
        mock_session.request.return_value = mock_response

        round_data = team_resource.create_round(tournament="TOC", side="A")

        assert isinstance(round_data, Round)
        assert round_data.tournament == "TOC"

    def test_cites(self, team_resource, mock_session):
        """Test getting team cites"""
        mock_response = Mock()
        mock_response.json.return_value = [{"title": "Healthcare", "cites": "Aff wins"}]
        mock_session.request.return_value = mock_response

        cites = team_resource.cites()

        assert len(cites) == 1
        assert isinstance(cites[0], Cite)
        assert cites[0].title == "Healthcare"

    def test_create_cite(self, team_resource, mock_session):
        """Test creating a cite"""
        mock_response = Mock()
        mock_response.json.return_value = {"title": "New Arg", "cites": "Some evidence"}
        mock_session.request.return_value = mock_response

        cite = team_resource.create_cite(title="New Arg", cites="Some evidence")

        assert isinstance(cite, Cite)
        assert cite.title == "New Arg"

    def test_history(self, team_resource, mock_session):
        """Test getting team history"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "description": "Added round",
                "updated_by": "user@example.com",
                "updated_at": "2025-11-18T10:00:00Z",
            }
        ]
        mock_session.request.return_value = mock_response

        history = team_resource.history()

        assert len(history) == 1
        assert isinstance(history[0], History)
        assert history[0].description == "Added round"


class TestRoundResource:
    @pytest.fixture
    def round_resource(self, mock_session):
        return RoundResource(mock_session, "hspolicy25", "NorthHollywood", "BeLu", "1")

    def test_get_round(self, round_resource, mock_session):
        """Test getting a specific round"""
        mock_response = Mock()
        mock_response.json.return_value = {"tournament": "TOC", "side": "A"}
        mock_session.request.return_value = mock_response

        round_data = round_resource.get()

        assert isinstance(round_data, Round)
        assert round_data.tournament == "TOC"

    def test_update_round(self, round_resource, mock_session):
        """Test updating a round"""
        mock_response = Mock()
        mock_response.json.return_value = {"tournament": "TOC", "report": "Updated"}
        mock_session.request.return_value = mock_response

        round_data = round_resource.update(report="Updated")

        assert isinstance(round_data, Round)
        assert round_data.report == "Updated"

    def test_delete_round(self, round_resource, mock_session):
        """Test deleting a round"""
        mock_response = Mock()
        mock_response.content = None
        mock_session.request.return_value = mock_response

        round_resource.delete()

        mock_session.request.assert_called_once()


class TestCiteResource:
    @pytest.fixture
    def cite_resource(self, mock_session):
        return CiteResource(mock_session, "hspolicy25", "NorthHollywood", "BeLu", "1")

    def test_delete_cite(self, cite_resource, mock_session):
        """Test deleting a cite"""
        mock_response = Mock()
        mock_response.content = None
        mock_session.request.return_value = mock_response

        cite_resource.delete()

        mock_session.request.assert_called_once()


class TestErrorHandling:
    def test_network_error(self, client, mock_session):
        """Test handling of network errors"""
        mock_session.get.side_effect = requests.exceptions.RequestException(
            "Network error"
        )

        with pytest.raises(APIError):
            client.caselists()
