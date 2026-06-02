from typing import Optional
from pydantic import BaseModel, Field


class CaptchaResponse(BaseModel):
    captcha_id: str
    captcha_text: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)
    captcha_id: str
    captcha_code: str = Field(..., min_length=4, max_length=4)


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha_id: str
    captcha_code: str = Field(..., min_length=4, max_length=4)


class AuthResponse(BaseModel):
    user_id: int
    username: str
    token: str
    student_id: Optional[int] = None


class UserInfo(BaseModel):
    id: int
    username: str
    avatar: str = ""
    created_at: str = ""
    student_id: Optional[int] = None
    has_profile: bool = False


class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4, max_length=128)


class UpdateAvatarRequest(BaseModel):
    avatar: str = Field(..., min_length=0)
