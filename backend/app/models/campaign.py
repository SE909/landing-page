from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class ModuleItem(BaseModel):
    title: str
    description: str
    duration: str


class Testimonial(BaseModel):
    name: str
    text: str
    rating: int = Field(ge=1, le=5)


class UserInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    bio: str
    photo_url: Optional[str] = None


class FormationInfo(BaseModel):
    name: str
    category: str
    target_audience: str
    level: str
    duration_hours: int
    format: str
    short_description: str
    objectives: str
    modules: list[ModuleItem]
    price: float
    currency: str = "EUR"
    bonuses: Optional[str] = None
    start_date: Optional[str] = None


class BrandingInfo(BaseModel):
    tone: str
    ai_model: str = "ollama"
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"
    style: str


class SocialProof(BaseModel):
    testimonials: list[Testimonial] = []
    stats: Optional[str] = None


class CampaignCreate(BaseModel):
    user_info: UserInfo
    formation: FormationInfo
    branding: BrandingInfo
    social_proof: SocialProof = SocialProof()


class CampaignResponse(CampaignCreate):
    id: str
    page_state: Optional[dict[str, Any]] = None
    generated_html: Optional[str] = None
    status: str = "draft"
    created_at: datetime
    updated_at: datetime
