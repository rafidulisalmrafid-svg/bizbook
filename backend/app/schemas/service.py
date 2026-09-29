from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ServiceCreate(BaseModel):
    title: str
    category: str = "General"
    description: Optional[str] = None
    deliverables: List[str] = []
    typical_duration: Optional[str] = None
    standard_price: float = 0.0

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    deliverables: Optional[List[str]] = None
    typical_duration: Optional[str] = None
    standard_price: Optional[float] = None
    is_active: Optional[bool] = None

class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    title: str
    category: str
    description: Optional[str] = None
    deliverables: List[str] = []
    typical_duration: Optional[str] = None
    standard_price: float
    is_active: bool
    is_archived: bool
    created_at: datetime

class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    created_at: datetime
