from pydantic import BaseModel


class PathGenerateRequest(BaseModel):
    student_id: int
    course_goal: str = ""


class PathGenerateResponse(BaseModel):
    student_id: int
    path_id: int
    path: dict


class PathListResponse(BaseModel):
    student_id: int
    paths: list[dict]
