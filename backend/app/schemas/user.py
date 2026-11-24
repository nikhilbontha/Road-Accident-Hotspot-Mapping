from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    organisation: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., description="admin, police_officer, safety_analyst, authority_official, public_viewer")


class UserRegister(UserBase):
    password: str = Field(..., min_length=10, description="At least 10 characters")
    policy_agreement: bool = Field(True, description="I will handle accident data under my department's policy")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=10)
    status: Optional[str] = "active"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    organisation: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class UserOut(UserBase):
    id: str
    status: str
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
