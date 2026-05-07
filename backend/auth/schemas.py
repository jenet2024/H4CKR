from pydantic import BaseModel, EmailStr, Field , field_validator
from typing import Optional
from datetime import datetime


# class RegisterRequest(BaseModel):
#     pseudo: str = Field(..., min_length=3, max_length=50)
#     email: EmailStr
#     password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    pseudo: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


    @field_validator("password")
    def check_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne doit pas dépasser 72 caractères.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    pseudo: str
    email: str
    avatar_url: Optional[str] = None
    is_admin: bool = False
    auth_provider: str
    created_at: datetime

    class Config:
        from_attributes = True


class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


TokenResponse.model_rebuild()
