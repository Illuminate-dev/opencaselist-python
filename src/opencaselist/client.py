"""Fluent API client for OpenCaselist"""

import os
import sys
from getpass import getpass
from typing import Any, Dict, List, Optional

import requests
from pydantic import ValidationError as PydanticValidationError

from .exceptions import APIError, AuthenticationError, NotFoundError, ValidationError
from .models import (
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


class BaseResource:
    """Base class for API resources with common functionality"""

    BASE_URL = "https://api.opencaselist.com/v1"

    def __init__(self, session: requests.Session):
        self._session = session

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an API request and handle errors"""
        url = f"{self.BASE_URL}{path}"

        try:
            response = self._session.request(
                method, url, params=params, json=json, timeout=30
            )
            response.raise_for_status()

            # Return JSON if available, otherwise return response
            if response.content:
                return response.json()
            return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif e.response.status_code == 404:
                raise NotFoundError(f"Resource not found: {path}")
            else:
                raise APIError(
                    f"API request failed: {e}", status_code=e.response.status_code
                )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {e}")


class RoundResource(BaseResource):
    """Resource for individual round operations"""

    def __init__(
        self,
        session: requests.Session,
        caselist: str,
        school: str,
        team: str,
        round_id: str,
    ):
        super().__init__(session)
        self.caselist = caselist
        self.school = school
        self.team = team
        self.round_id = round_id
        self._path = (
            f"/caselists/{caselist}/schools/{school}/teams/{team}/rounds/{round_id}"
        )

    def get(self) -> Round:
        """Get a specific round"""
        data = self._request("GET", self._path)
        return Round(**data)

    def update(self, **kwargs) -> Round:
        """Update a round"""
        data = self._request("PUT", self._path, json=kwargs)
        return Round(**data)

    def delete(self) -> None:
        """Delete a round"""
        self._request("DELETE", self._path)


class CiteResource(BaseResource):
    """Resource for individual cite operations"""

    def __init__(
        self,
        session: requests.Session,
        caselist: str,
        school: str,
        team: str,
        cite_id: str,
    ):
        super().__init__(session)
        self.caselist = caselist
        self.school = school
        self.team = team
        self.cite_id = cite_id
        self._path = (
            f"/caselists/{caselist}/schools/{school}/teams/{team}/cites/{cite_id}"
        )

    def delete(self) -> None:
        """Delete a cite"""
        self._request("DELETE", self._path)


class TeamResource(BaseResource):
    """Resource for team operations"""

    def __init__(
        self, session: requests.Session, caselist: str, school: str, team: str
    ):
        super().__init__(session)
        self.caselist = caselist
        self.school = school
        self.team = team
        self._path = f"/caselists/{caselist}/schools/{school}/teams/{team}"

    def get(self) -> Team:
        """Get team details"""
        data = self._request("GET", self._path)
        return Team(**data)

    def patch(self, **kwargs) -> Team:
        """Update team details"""
        data = self._request("PATCH", self._path, json=kwargs)
        return Team(**data)

    def delete(self) -> None:
        """Delete a team"""
        self._request("DELETE", self._path)

    def rounds(self, side: Optional[str] = None) -> List[Round]:
        """
        Get all rounds for this team

        Args:
            side: 'A' for aff rounds, 'N' for neg rounds, None for all rounds
        """
        params = {}
        if side:
            params["side"] = side

        data = self._request("GET", f"{self._path}/rounds", params=params)
        return [Round(**round_data) for round_data in data]

    def round(self, round_id: str) -> RoundResource:
        """Get a specific round resource"""
        return RoundResource(
            self._session, self.caselist, self.school, self.team, round_id
        )

    def create_round(self, **kwargs) -> Round:
        """Create a new round for this team"""
        data = self._request("POST", f"{self._path}/rounds", json=kwargs)
        return Round(**data)

    def cites(self) -> List[Cite]:
        """Get all cites for this team"""
        data = self._request("GET", f"{self._path}/cites")
        return [Cite(**cite_data) for cite_data in data]

    def cite(self, cite_id: str) -> CiteResource:
        """Get a specific cite resource"""
        return CiteResource(
            self._session, self.caselist, self.school, self.team, cite_id
        )

    def create_cite(self, **kwargs) -> Cite:
        """Create a new cite for this team"""
        data = self._request("POST", f"{self._path}/cites", json=kwargs)
        return Cite(**data)

    def history(self) -> List[History]:
        """Get history log for this team"""
        data = self._request("GET", f"{self._path}/history")
        return [History(**entry) for entry in data]


class SchoolResource(BaseResource):
    """Resource for school operations"""

    def __init__(self, session: requests.Session, caselist: str, school: str):
        super().__init__(session)
        self.caselist = caselist
        self.school = school
        self._path = f"/caselists/{caselist}/schools/{school}"

    def get(self) -> School:
        """Get school details"""
        data = self._request("GET", self._path)
        return School(**data)

    def teams(self) -> List[Team]:
        """Get all teams in this school"""
        data = self._request("GET", f"{self._path}/teams")
        return [Team(**team_data) for team_data in data]

    def team(self, team: str) -> TeamResource:
        """Get a specific team resource"""
        return TeamResource(self._session, self.caselist, self.school, team)

    def create_team(self, **kwargs) -> Team:
        """Create a new team in this school"""
        data = self._request("POST", f"{self._path}/teams", json=kwargs)
        return Team(**data)

    def history(self) -> List[History]:
        """Get history log for this school"""
        data = self._request("GET", f"{self._path}/history")
        return [History(**entry) for entry in data]


class CaselistResource(BaseResource):
    """Resource for caselist operations"""

    def __init__(self, session: requests.Session, caselist: str):
        super().__init__(session)
        self.caselist = caselist
        self._path = f"/caselists/{caselist}"

    def get(self) -> Caselist:
        """Get caselist details"""
        data = self._request("GET", self._path)
        return Caselist(**data)

    def schools(self) -> List[School]:
        """Get all schools in this caselist"""
        data = self._request("GET", f"{self._path}/schools")
        return [School(**school_data) for school_data in data]

    def school(self, school: str) -> SchoolResource:
        """Get a specific school resource"""
        return SchoolResource(self._session, self.caselist, school)

    def create_school(self, **kwargs) -> School:
        """Create a new school in this caselist"""
        data = self._request("POST", f"{self._path}/schools", json=kwargs)
        return School(**data)

    def recent(self) -> List[Recent]:
        """Get recent modifications in this caselist"""
        data = self._request("GET", f"{self._path}/recent")
        return [Recent(**entry) for entry in data]

    def downloads(self) -> List[Download]:
        """Get bulk downloads for this caselist"""
        data = self._request("GET", f"{self._path}/downloads")
        return [Download(**entry) for entry in data]


class OpenCaselistClient:
    """
    Fluent API client for OpenCaselist

    Example usage:
        client = OpenCaselistClient(username="user", password="pass")

        # Get rounds for a team
        rounds = client.caselist("hspolicy25").school("Greenhill").team("JL").rounds()

        # Get all schools
        schools = client.caselist("hspolicy25").schools()

        # Create a round
        client.caselist("hspolicy25").school("Greenhill").team("JL").create_round(
            tournament="TOC",
            side="A",
            opponent="Westminster KN"
        )
    """

    BASE_URL = "https://api.opencaselist.com/v1"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auto_login: bool = True,
    ):
        """
        Initialize the OpenCaselist API client

        Args:
            username: OpenCaselist username (will prompt if not provided)
            password: OpenCaselist password (will prompt if not provided)
            auto_login: Whether to automatically login on initialization
        """
        self._session = requests.Session()
        self._authenticated = False

        if auto_login:
            self.login(username, password)

    def login(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> bool:
        """
        Authenticate with the OpenCaselist API

        Args:
            username: OpenCaselist username
            password: OpenCaselist password

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        # Get credentials from environment variables if not provided
        username = username or os.getenv("OPENCASELIST_USER")
        password = password or os.getenv("OPENCASELIST_PASSWORD")

        # Prompt for credentials if still not available
        if not username:
            username = input("OpenCaselist username: ")
        if not password:
            password = getpass("OpenCaselist password: ")

        login_url = f"{self.BASE_URL}/login"

        try:
            response = self._session.post(
                login_url, json={"username": username, "password": password}, timeout=30
            )
            response.raise_for_status()

            self._authenticated = True
            print("✓ Successfully authenticated with OpenCaselist API")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid username or password")
            else:
                raise APIError(
                    f"Error during login: {e}", status_code=e.response.status_code
                )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error during login: {e}")

    def caselist(self, caselist: str) -> CaselistResource:
        """
        Get a caselist resource

        Args:
            caselist: Caselist slug (e.g., 'hspolicy25', 'hsld24')

        Returns:
            CaselistResource for further chaining
        """
        return CaselistResource(self._session, caselist)

    def caselists(self) -> List[Caselist]:
        """Get all available caselists"""
        url = f"{self.BASE_URL}/caselists"
        try:
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [Caselist(**caselist_data) for caselist_data in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch caselists: {e}")

    def search(self, query: str, **params) -> List[SearchResult]:
        """
        Search across caselists

        Args:
            query: Search query
            **params: Additional search parameters

        Returns:
            List of SearchResult objects
        """
        url = f"{self.BASE_URL}/search"
        params["q"] = query
        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [SearchResult(**result) for result in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Search failed: {e}")

    def download(self, **params) -> bytes:
        """
        Download a file

        Args:
            **params: Download parameters

        Returns:
            File content as bytes
        """
        url = f"{self.BASE_URL}/download"
        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise APIError(f"Download failed: {e}")

    # Tabroom methods
    def tabroom_students(self) -> List[TabroomStudent]:
        """
        Get list of students linked to the authenticated user on Tabroom

        Returns:
            List of TabroomStudent objects
        """
        url = f"{self.BASE_URL}/tabroom/students"
        try:
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [TabroomStudent(**student) for student in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch Tabroom students: {e}")

    def tabroom_rounds(self, slug: Optional[str] = None) -> List[TabroomRound]:
        """
        Get list of rounds linked to the authenticated user or slug on Tabroom

        Args:
            slug: Optional slug to filter rounds

        Returns:
            List of TabroomRound objects
        """
        url = f"{self.BASE_URL}/tabroom/rounds"
        params = {}
        if slug:
            params["slug"] = slug

        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [TabroomRound(**round_data) for round_data in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch Tabroom rounds: {e}")

    def tabroom_chapters(self) -> List[TabroomChapter]:
        """
        Get list of chapters linked to the authenticated user on Tabroom

        Returns:
            List of TabroomChapter objects
        """
        url = f"{self.BASE_URL}/tabroom/chapters"
        try:
            response = self._session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [TabroomChapter(**chapter) for chapter in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch Tabroom chapters: {e}")

    def create_tabroom_link(self, **kwargs) -> TabroomLink:
        """
        Create a tabroom link

        Args:
            **kwargs: Link data (e.g., slug)

        Returns:
            TabroomLink object
        """
        url = f"{self.BASE_URL}/tabroom/link"
        try:
            response = self._session.post(url, json=kwargs, timeout=30)
            response.raise_for_status()
            data = response.json()
            return TabroomLink(**data)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create Tabroom link: {e}")

    # OpenEv methods
    def openev_files(self, year: Optional[str] = None, **params) -> List[File]:
        """
        Get files for an open evidence year

        Args:
            year: Optional year to filter files
            **params: Additional query parameters

        Returns:
            List of File objects
        """
        url = f"{self.BASE_URL}/openev"
        if year:
            params["year"] = year

        try:
            response = self._session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [File(**file_data) for file_data in data]
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to fetch OpenEv files: {e}")

    def create_openev_file(self, **kwargs) -> File:
        """
        Create an OpenEv file

        Args:
            **kwargs: File data (title, path, year, camp, lab, tags, etc.)

        Returns:
            File object
        """
        url = f"{self.BASE_URL}/openev"
        try:
            response = self._session.post(url, json=kwargs, timeout=30)
            response.raise_for_status()
            data = response.json()
            return File(**data)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create OpenEv file: {e}")

    def delete_openev_file(self, file_id: int) -> None:
        """
        Delete an OpenEv file

        Args:
            file_id: The ID of the file to delete
        """
        url = f"{self.BASE_URL}/openev/{file_id}"
        try:
            response = self._session.delete(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to delete OpenEv file: {e}")
