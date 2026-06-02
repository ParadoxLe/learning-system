import json
from sqlalchemy.orm import Session
from backend.models.resource import LearningResource
from backend.agents.resource_agents.doc_agent import DocAgent
from backend.agents.resource_agents.mindmap_agent import MindMapAgent
from backend.agents.resource_agents.exercise_agent import ExerciseAgent
from backend.agents.resource_agents.reading_agent import ReadingAgent
from backend.agents.resource_agents.video_agent import VideoAgent
from backend.agents.resource_agents.code_agent import CodeAgent
from backend.services.profile_service import ProfileService


class ResourceService:
    def __init__(self):
        self.doc_agent = DocAgent()
        self.mindmap_agent = MindMapAgent()
        self.exercise_agent = ExerciseAgent()
        self.reading_agent = ReadingAgent()
        self.video_agent = VideoAgent()
        self.code_agent = CodeAgent()
        self.profile_service = ProfileService()

    def generate_resources(
        self,
        db: Session,
        student_id: int,
        resource_types: list[str],
        course_topic: str,
        tech_stack: str = "",
        difficulty: str = "medium",
    ) -> list[dict]:
        """Generate resources using multiple agents, save to DB, return results."""
        # Get student profile
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        results = []

        for res_type in resource_types:
            try:
                content, title = self._generate_one(res_type, profile, course_topic, tech_stack, difficulty)
                resource = self._save_resource(db, student_id, res_type, title, content)
                results.append({
                    "id": resource.id,
                    "resource_type": resource.resource_type,
                    "title": resource.title,
                    "content": resource.content,
                })
            except Exception as e:
                results.append({
                    "id": -1,
                    "resource_type": res_type,
                    "title": f"生成失败: {res_type}",
                    "content": str(e),
                })

        # Auto-update profile: record the topic being learned
        if profile and results:
            self._auto_update_profile(db, student_id, profile, course_topic, resource_types)

        return results

    def _auto_update_profile(self, db: Session, student_id: int, profile: dict,
                             course_topic: str, resource_types: list[str]):
        """Mark the learning topic in profile so the mind map reflects latest activity."""
        kb = profile.setdefault("knowledge_base", {})

        # Add to target topics if new
        existing_targets = set(kb.get("target_topics", []))
        if course_topic and course_topic not in existing_targets:
            existing_targets.add(course_topic)
            kb["target_topics"] = list(existing_targets)

        # Add new modalities
        pm = profile.setdefault("preferred_modalities", {})
        existing_mods = set(pm.get("modalities", []) if isinstance(pm, dict) else pm)
        if isinstance(pm, dict):
            for rt in resource_types:
                if rt not in existing_mods:
                    existing_mods.add(rt)
            pm["modalities"] = list(existing_mods)

        self.profile_service._save_profile(db, student_id, profile)

    def _generate_one(self, res_type: str, profile: dict, course_topic: str,
                      tech_stack: str, difficulty: str) -> tuple[str, str]:
        """Call the appropriate agent and return (content, title)."""
        if res_type == "doc":
            content = self.doc_agent.generate(profile, course_topic)
            title = f"课程讲解：{course_topic}"
        elif res_type == "mindmap":
            content = self.mindmap_agent.generate(course_topic)
            title = f"思维导图：{course_topic}"
        elif res_type == "exercise":
            content = self.exercise_agent.generate(profile, course_topic, difficulty)
            title = f"练习题：{course_topic}"
        elif res_type == "reading":
            content = self.reading_agent.generate(profile, course_topic)
            title = f"拓展阅读：{course_topic}"
        elif res_type == "video_script":
            content = self.video_agent.generate(profile, course_topic)
            title = f"视频脚本：{course_topic}"
        elif res_type == "code_case":
            content = self.code_agent.generate(profile, tech_stack, course_topic)
            title = f"代码案例：{course_topic or tech_stack}"
        else:
            raise ValueError(f"Unknown resource type: {res_type}")

        return content, title

    def _save_resource(self, db: Session, student_id: int, res_type: str,
                       title: str, content: str) -> LearningResource:
        resource = LearningResource(
            student_id=student_id,
            resource_type=res_type,
            title=title,
            content=content,
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return resource

    def get_resources(self, db: Session, student_id: int, res_type: str = None) -> list[dict]:
        """Get all resources for a student, optionally filtered by type."""
        query = db.query(LearningResource).filter(LearningResource.student_id == student_id)
        if res_type:
            query = query.filter(LearningResource.resource_type == res_type)
        resources = query.order_by(LearningResource.created_at.desc()).all()

        return [
            {
                "id": r.id,
                "resource_type": r.resource_type,
                "title": r.title,
                "content": r.content,
                "metadata": json.loads(r.metadata_json) if r.metadata_json else {},
            }
            for r in resources
        ]

    def delete_resource(self, db: Session, student_id: int, resource_id: int) -> bool:
        """Delete a resource by id."""
        resource = (
            db.query(LearningResource)
            .filter(LearningResource.id == resource_id, LearningResource.student_id == student_id)
            .first()
        )
        if not resource:
            return False
        db.delete(resource)
        db.commit()
        return True

    def complete_resource(self, db: Session, student_id: int, resource_id: int) -> dict:
        """Mark a resource as completed and update profile."""
        resource = (
            db.query(LearningResource)
            .filter(LearningResource.id == resource_id, LearningResource.student_id == student_id)
            .first()
        )
        if not resource:
            return {"ok": False, "message": "资源不存在"}

        # Update profile
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        if profile and resource.title:
            kb = profile.setdefault("knowledge_base", {})
            weak = kb.get("weak_points", [])
            mastered = list(kb.get("mastered_topics", []))

            # Extract the topic from the title (format: "类型：主题")
            topic = resource.title.split("：", 1)[-1] if "：" in resource.title else resource.title

            if topic in weak:
                weak.remove(topic)
                kb["weak_points"] = weak
            if topic not in mastered:
                mastered.append(topic)
                kb["mastered_topics"] = mastered

            # Bump level
            if len(mastered) >= 8:
                kb["level"] = "advanced"
            elif len(mastered) >= 4:
                kb["level"] = "intermediate"

            self.profile_service._save_profile(db, student_id, profile)

        return {"ok": True, "topic": resource.title, "profile_updated": profile is not None}
