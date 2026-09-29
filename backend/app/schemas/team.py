from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class TeamExperienceCreate(BaseModel):
    title: str
    organization: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class TeamExperienceRead(TeamExperienceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_member_id: str
    created_at: datetime

class TeamCertificationCreate(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

class TeamCertificationRead(TeamCertificationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    team_member_id: str
    created_at: datetime

class TeamMemberCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    designation: str
    department: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    joined_date: Optional[datetime] = None

class TeamMemberUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    is_active: Optional[bool] = None

class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    user_id: Optional[str] = None
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    designation: str
    department: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    is_active: bool
    is_archived: bool
    created_at: datetime
    experiences: List[TeamExperienceRead] = []
    certifications: List[TeamCertificationRead] = []
