from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.business import ClientStatusEnum

class ClientContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False

class ClientContactRead(ClientContactCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    created_at: datetime

class ClientCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    status: ClientStatusEnum = ClientStatusEnum.ACTIVE
    address: Optional[str] = None
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    status: Optional[ClientStatusEnum] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    status: ClientStatusEnum
    address: Optional[str] = None
    notes: Optional[str] = None
    is_archived: bool
    created_at: datetime
    contacts: List[ClientContactRead] = []
