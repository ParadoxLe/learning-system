from typing import Optional
from pydantic import BaseModel


class ProfileChatRequest(BaseModel):
    student_id: int
    message: str


class ProfileChatResponse(BaseModel):
    status: str  # "need_more_info" | "complete"
    message: str = ""
    profile: Optional[dict] = None


class ProfileResponse(BaseModel):
    student_id: int
    profile: dict
    version: int
