"""Pydantic models for OpenCaselist API resources"""

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Caselist(BaseModel):
    """Represents a caselist (e.g., hspolicy25, hsld24, etc.)"""

    caselist_id: Optional[int] = None
    slug: str
    name: str
    event: Optional[str] = None
    year: Optional[int] = None
    archived: Optional[bool] = None


class School(BaseModel):
    """Represents a school in a caselist"""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    state: Optional[str] = None


class Team(BaseModel):
    """Represents a debate team"""

    name: str
    display_name: Optional[str] = None
    notes: Optional[str] = None

    # Debater 1
    debater1_first: Optional[str] = None
    debater1_last: Optional[str] = None
    debater1_student_id: Optional[int] = None

    # Debater 2
    debater2_first: Optional[str] = None
    debater2_last: Optional[str] = None
    debater2_student_id: Optional[int] = None

    # Debater 3
    debater3_first: Optional[str] = None
    debater3_last: Optional[str] = None
    debater3_student_id: Optional[int] = None

    # Debater 4
    debater4_first: Optional[str] = None
    debater4_last: Optional[str] = None
    debater4_student_id: Optional[int] = None


class Round(BaseModel):
    """Represents a debate round"""

    tournament: Optional[str] = None
    side: Optional[str] = None  # 'A' for aff, 'N' for neg
    round: Optional[str] = None
    opponent: Optional[str] = None
    judge: Optional[str] = None
    report: Optional[str] = None
    tourn_id: Optional[int] = None
    external_id: Optional[int] = None


class Cite(BaseModel):
    """Represents a citation/evidence cite"""

    cite_id: Optional[int] = None
    round_id: Optional[int] = None
    title: Optional[str] = None
    cites: Optional[str] = None


class TabroomStudent(BaseModel):
    """Represents a Tabroom student linked to a user"""

    id: Optional[int] = None
    first: Optional[str] = None
    last: Optional[str] = None


class TabroomRound(BaseModel):
    """Represents a Tabroom round linked to a user or slug"""

    id: Optional[int] = None
    tournament: Optional[str] = None
    round: Optional[str] = None
    side: Optional[str] = None
    opponent: Optional[str] = None
    judge: Optional[str] = None
    start_time: Optional[str] = None
    share: Optional[str] = None


class TabroomChapter(BaseModel):
    """Represents a Tabroom chapter linked to a user"""

    id: Optional[int] = None
    name: Optional[str] = None


class TabroomLink(BaseModel):
    """Represents a Tabroom link created via POST /tabroom/link"""

    slug: Optional[str] = None


class File(BaseModel):
    """Represents an OpenEv file"""

    openev_id: Optional[int] = None
    title: Optional[str] = None
    path: Optional[str] = None
    year: Optional[str] = None
    camp: Optional[str] = None
    lab: Optional[str] = None
    tags: Optional[List[str]] = None
    file: Optional[str] = None
    filename: Optional[str] = None


class SearchResult(BaseModel):
    """Represents a search result from the /search endpoint"""

    id: Optional[int] = None
    shard: Optional[str] = None
    content: Optional[str] = None
    path: Optional[str] = None


class Download(BaseModel):
    """Represents a bulk download from the /caselists/{caselist}/downloads endpoint"""

    name: Optional[str] = None
    url: Optional[str] = None


class History(BaseModel):
    """Represents a history log entry from school or team history endpoints"""

    description: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None


class Recent(BaseModel):
    """Represents a recent modification from the /caselists/{caselist}/recent endpoint"""

    team_id: Optional[int] = None
    side: Optional[str] = None
    tournament: Optional[str] = None
    round: Optional[str] = None
    opponent: Optional[str] = None
    opensource: Optional[str] = None
    team_name: Optional[str] = None
    team_display_name: Optional[str] = None
    school_name: Optional[str] = None
    school_display_name: Optional[str] = None
    updated_at: Optional[str] = None


class Update(BaseModel):
    """Represents an update (empty schema)"""

    pass


class Err(BaseModel):
    """Represents an error response from the API"""

    message: str
