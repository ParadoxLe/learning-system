from pydantic import BaseModel


class ResourceGenerateRequest(BaseModel):
    student_id: int
    resource_types: list[str] = ["doc", "mindmap", "exercise", "reading", "video_script", "code_case"]
    course_topic: str = ""  # 课程主题
    tech_stack: str = ""    # 技术栈（code_case 用）
    difficulty: str = "medium"


class ResourceItem(BaseModel):
    id: int
    resource_type: str
    title: str
    content: str
    metadata: dict = {}


class ResourceGenerateResponse(BaseModel):
    student_id: int
    resources: list[ResourceItem]


class ResourceListResponse(BaseModel):
    student_id: int
    resources: list[ResourceItem]
