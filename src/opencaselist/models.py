"""Pydantic models for OpenCaselist API resources"""

from typing import Optional
from pydantic import BaseModel, Field


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

    name: str
    display_name: Optional[str] = Field(None, alias="displayName")
    state: Optional[str] = None

    class Config:
        populate_by_name = True  # Allow both 'display_name' and 'displayName'


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
    """Represents a Tabroom student"""

    # Schema not provided yet - will be populated when available
    pass


class TabroomRound(BaseModel):
    """Represents a Tabroom round"""

    # Schema not provided yet - will be populated when available
    pass


class TabroomChapter(BaseModel):
    """Represents a Tabroom chapter"""

    # Schema not provided yet - will be populated when available
    pass


class TabroomLink(BaseModel):
    """Represents a Tabroom link"""

    # Schema not provided yet - will be populated when available
    pass


class File(BaseModel):
    """Represents an OpenEv file"""

    # Schema not provided yet - will be populated when available
    pass


class SearchResult(BaseModel):
    """Represents a search result"""

    # Schema not provided yet - will be populated when available
    pass


class Download(BaseModel):
    """Represents a bulk download"""

    # Schema not provided yet - will be populated when available
    pass


class History(BaseModel):
    """Represents a history log entry"""

    # Schema not provided yet - will be populated when available
    pass


class Recent(BaseModel):
    """Represents a recent modification"""

    # Schema not provided yet - will be populated when available
    pass


class Update(BaseModel):
    """Represents an update"""

    # Schema not provided yet - will be populated when available
    pass
