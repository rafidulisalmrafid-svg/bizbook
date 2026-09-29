from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CompanyProfileUpdate(BaseModel):
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    established_year: Optional[int] = None
    legal_structure: Optional[str] = None
    primary_industry: Optional[str] = None
    overview: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    annual_turnover: Optional[str] = None

class CompanyProfileRead(CompanyProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime

class CompanyBrandUpdate(BaseModel):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    font_family: Optional[str] = None
    logo_url: Optional[str] = None
    dark_logo_url: Optional[str] = None
    icon_url: Optional[str] = None

class CompanyBrandRead(CompanyBrandUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime

class CompanyContactCreate(BaseModel):
    contact_type: str = "email"
    label: str
    value: str
    is_primary: bool = False

class CompanyContactRead(CompanyContactCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime

class CompanyLetterheadCreate(BaseModel):
    title: str = "Corporate Letterhead"
    header_html: Optional[str] = None
    footer_html: Optional[str] = None
    margin_top_mm: int = 25
    margin_bottom_mm: int = 25
    is_default: bool = True

class CompanyLetterheadRead(CompanyLetterheadCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime

class CompanySignatureCreate(BaseModel):
    name: str
    designation: str
    signature_image_url: str
    is_active: bool = True

class CompanySignatureRead(CompanySignatureCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    user_id: Optional[str] = None
    created_at: datetime

class CompanySealCreate(BaseModel):
    name: str
    seal_image_url: str
    is_active: bool = True

class CompanySealRead(CompanySealCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime

class PartnerLogoCreate(BaseModel):
    partner_name: str
    logo_url: str
    sort_order: int = 0

class PartnerLogoRead(PartnerLogoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    created_at: datetime

class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    domain: Optional[str] = None
    is_active: bool
    created_at: datetime
    profile: Optional[CompanyProfileRead] = None
    brand: Optional[CompanyBrandRead] = None
