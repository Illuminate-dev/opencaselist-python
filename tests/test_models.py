"""Tests for Pydantic models"""

import pytest
from opencaselist.models import (
    Caselist,
    Cite,
    Download,
    Err,
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
    Update,
)


class TestCaselist:
    def test_caselist_creation(self):
        caselist = Caselist(slug="hspolicy25", name="HS Policy 2025")
        assert caselist.slug == "hspolicy25"
        assert caselist.name == "HS Policy 2025"

    def test_caselist_with_all_fields(self):
        caselist = Caselist(
            caselist_id=1,
            slug="hspolicy25",
            name="HS Policy 2025",
            event="Policy",
            year=2025,
            archived=False,
        )
        assert caselist.caselist_id == 1
        assert caselist.year == 2025
        assert caselist.archived is False


class TestSchool:
    def test_school_creation(self):
        school = School(name="Greenhill")
        assert school.name == "Greenhill"
        assert school.display_name is None

    def test_school_with_display_name(self):
        school = School(name="greenhill", display_name="Greenhill", state="TX")
        assert school.name == "greenhill"
        assert school.display_name == "Greenhill"
        assert school.state == "TX"

    def test_school_display_name_alias(self):
        # Test that displayName alias works
        school = School(name="greenhill", displayName="Greenhill")
        assert school.display_name == "Greenhill"


class TestTeam:
    def test_team_creation(self):
        team = Team(name="JL")
        assert team.name == "JL"

    def test_team_with_debaters(self):
        team = Team(
            name="JL",
            display_name="Johnson-Lee",
            debater1_first="John",
            debater1_last="Johnson",
            debater1_student_id=123,
            debater2_first="Jane",
            debater2_last="Lee",
            debater2_student_id=456,
        )
        assert team.debater1_first == "John"
        assert team.debater1_last == "Johnson"
        assert team.debater2_first == "Jane"


class TestRound:
    def test_round_creation(self):
        round_data = Round(
            tournament="TOC",
            side="A",
            round="Quarters",
            opponent="Westminster KN",
            judge="John Doe",
        )
        assert round_data.tournament == "TOC"
        assert round_data.side == "A"
        assert round_data.opponent == "Westminster KN"

    def test_round_with_ids(self):
        round_data = Round(
            tournament="TOC", tourn_id=100, external_id=200, report="2AC dropped T"
        )
        assert round_data.tourn_id == 100
        assert round_data.external_id == 200


class TestCite:
    def test_cite_creation(self):
        cite = Cite(title="Healthcare", cites="Aff said healthcare good")
        assert cite.title == "Healthcare"
        assert cite.cites == "Aff said healthcare good"

    def test_cite_with_ids(self):
        cite = Cite(cite_id=1, round_id=10, title="Healthcare")
        assert cite.cite_id == 1
        assert cite.round_id == 10


class TestTabroomStudent:
    def test_tabroom_student_creation(self):
        student = TabroomStudent(id=123, first="John", last="Doe")
        assert student.id == 123
        assert student.first == "John"
        assert student.last == "Doe"

    def test_tabroom_student_optional_fields(self):
        student = TabroomStudent()
        assert student.id is None
        assert student.first is None


class TestTabroomRound:
    def test_tabroom_round_creation(self):
        round_data = TabroomRound(
            id=1,
            tournament="TOC",
            round="Quarters",
            side="A",
            opponent="Westminster",
            judge="John Doe",
            start_time="2025-11-18T10:00:00Z",
            share="public",
        )
        assert round_data.id == 1
        assert round_data.tournament == "TOC"
        assert round_data.start_time == "2025-11-18T10:00:00Z"
        assert round_data.share == "public"


class TestTabroomChapter:
    def test_tabroom_chapter_creation(self):
        chapter = TabroomChapter(id=1, name="Greenhill")
        assert chapter.id == 1
        assert chapter.name == "Greenhill"


class TestTabroomLink:
    def test_tabroom_link_creation(self):
        link = TabroomLink(slug="greenhill-jl")
        assert link.slug == "greenhill-jl"


class TestFile:
    def test_file_creation(self):
        file = File(
            openev_id=1,
            title="Debate Camp Cards",
            path="/files/2025/michigan/lab1/cards.docx",
            year="2025",
            camp="Michigan",
            lab="Lab 1",
            tags=["policy", "aff"],
            file="/uploads/file.docx",
            filename="cards.docx",
        )
        assert file.openev_id == 1
        assert file.title == "Debate Camp Cards"
        assert file.year == "2025"
        assert file.tags == ["policy", "aff"]
        assert file.filename == "cards.docx"

    def test_file_empty_tags(self):
        file = File(title="Test", tags=[])
        assert file.tags == []


class TestSearchResult:
    def test_search_result_creation(self):
        result = SearchResult(
            id=1,
            shard="hspolicy25",
            content="Some debate content",
            path="/caselists/hspolicy25/greenhill/jl",
        )
        assert result.id == 1
        assert result.shard == "hspolicy25"
        assert result.content == "Some debate content"


class TestDownload:
    def test_download_creation(self):
        download = Download(name="All Rounds", url="https://example.com/download.zip")
        assert download.name == "All Rounds"
        assert download.url == "https://example.com/download.zip"


class TestHistory:
    def test_history_creation(self):
        history = History(
            description="Added new round",
            updated_by="user@example.com",
            updated_at="2025-11-18T10:00:00Z",
        )
        assert history.description == "Added new round"
        assert history.updated_by == "user@example.com"
        assert history.updated_at == "2025-11-18T10:00:00Z"


class TestRecent:
    def test_recent_creation(self):
        recent = Recent(
            team_id=123,
            side="A",
            tournament="TOC",
            round="Quarters",
            opponent="Westminster KN",
            opensource="public",
            team_name="jl",
            team_display_name="Johnson-Lee",
            school_name="greenhill",
            school_display_name="Greenhill",
            updated_at="2025-11-18T10:00:00Z",
        )
        assert recent.team_id == 123
        assert recent.side == "A"
        assert recent.tournament == "TOC"
        assert recent.team_display_name == "Johnson-Lee"


class TestUpdate:
    def test_update_creation(self):
        # Update model is empty, just verify it can be instantiated
        update = Update()
        assert isinstance(update, Update)


class TestErr:
    def test_err_creation(self):
        err = Err(message="An error occurred")
        assert err.message == "An error occurred"

    def test_err_requires_message(self):
        # message is required, not optional
        with pytest.raises(Exception):
            Err()
