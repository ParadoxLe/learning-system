import datetime
import json
import re
from sqlalchemy.orm import Session
from backend.models.path import LearningPath
from backend.agents.path_agent import PathAgent
from backend.services.profile_service import ProfileService
from backend.services.resource_service import ResourceService


class PathService:
    def __init__(self):
        self.path_agent = PathAgent()
        self.profile_service = ProfileService()
        self.resource_service = ResourceService()

    def generate_path(self, db: Session, student_id: int, course_goal: str = "") -> dict:
        """Generate a learning path based on profile and available resources."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        resources = self.resource_service.get_resources(db, student_id)

        path_data = self.path_agent.plan(profile, resources, course_goal)

        # Match existing resources to path nodes
        path_data = self._match_resources(path_data, resources)

        path = LearningPath(
            student_id=student_id,
            title=path_data.get("title", f"学习路径 - {course_goal}"),
            nodes_json=json.dumps(path_data, ensure_ascii=False),
        )
        # Auto-update profile with path goal
        if profile and course_goal:
            kb = profile.setdefault("knowledge_base", {})
            existing = set(kb.get("target_topics", []))
            if course_goal not in existing:
                existing.add(course_goal)
                kb["target_topics"] = list(existing)
            self.profile_service._save_profile(db, student_id, profile)

        db.add(path)
        db.commit()
        db.refresh(path)

        return {"student_id": student_id, "path_id": path.id, "path": path_data}

    def generate_path_stream(self, db: Session, student_id: int, course_goal: str = ""):
        """Stream learning path generation."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        resources = self.resource_service.get_resources(db, student_id)

        path_data = None
        for item in self.path_agent.plan_stream(profile, resources, course_goal):
            if isinstance(item, dict):
                path_data = item
            else:
                yield item

        if path_data is None:
            yield {"error": "Failed to generate path"}
            return

        path_data = self._match_resources(path_data, resources)

        path = LearningPath(
            student_id=student_id,
            title=path_data.get("title", f"学习路径 - {course_goal}"),
            nodes_json=json.dumps(path_data, ensure_ascii=False),
        )
        # Auto-update profile with path goal
        if profile and course_goal:
            kb = profile.setdefault("knowledge_base", {})
            existing = set(kb.get("target_topics", []))
            if course_goal not in existing:
                existing.add(course_goal)
                kb["target_topics"] = list(existing)
            self.profile_service._save_profile(db, student_id, profile)

        db.add(path)
        db.commit()
        db.refresh(path)

        yield {"student_id": student_id, "path_id": path.id, "path": path_data}

    def _match_resources(self, path_data: dict, resources: list[dict]) -> dict:
        """For each path node, find matching existing resources by type + keyword overlap."""
        if not resources:
            return path_data

        for phase in path_data.get("phases", []):
            for node in phase.get("nodes", []):
                node_type = node.get("resource_type", "")
                node_title = node.get("title", "").lower()

                matching = [r for r in resources if r.get("resource_type") == node_type]
                if not matching:
                    continue

                node_words = set(re.findall(r'\w+', node_title))
                scored = []
                for r in matching:
                    r_title = r.get("title", "").lower()
                    r_words = set(re.findall(r'\w+', r_title))
                    overlap = len(node_words & r_words)
                    # Bonus for matching course topic keywords
                    r_content = r.get("content", "")[:500].lower()
                    for w in node_words:
                        if len(w) >= 2 and w in r_content:
                            overlap += 0.5
                    scored.append((overlap, r))

                scored.sort(key=lambda x: x[0], reverse=True)
                linked = [
                    {"id": r["id"], "title": r["title"], "resource_type": r["resource_type"]}
                    for score, r in scored[:3] if score > 0
                ]
                node["linked_resources"] = linked

        return path_data

    def get_paths(self, db: Session, student_id: int) -> list[dict]:
        """Get all learning paths for a student."""
        paths = (
            db.query(LearningPath)
            .filter(LearningPath.student_id == student_id)
            .order_by(LearningPath.created_at.desc())
            .all()
        )
        return [
            {
                "id": p.id,
                "title": p.title,
                "path": json.loads(p.nodes_json),
                "status": p.status,
                "created_at": str(p.created_at),
            }
            for p in paths
        ]

    def complete_node(self, db: Session, student_id: int, path_id: int, phase_idx: int, node_order: int) -> dict:
        """Mark a path node as completed and update profile accordingly."""
        path = (
            db.query(LearningPath)
            .filter(LearningPath.id == path_id, LearningPath.student_id == student_id)
            .first()
        )
        if not path:
            return {"ok": False, "message": "路径不存在"}

        path_data = json.loads(path.nodes_json)
        phases = path_data.get("phases", [])

        if phase_idx >= len(phases):
            return {"ok": False, "message": "阶段不存在"}

        node = None
        for n in phases[phase_idx].get("nodes", []):
            if n.get("order") == node_order:
                node = n
                break

        if not node:
            return {"ok": False, "message": "节点不存在"}

        if node.get("completed"):
            return {"ok": False, "message": "该节点已完成，无需重复确认"}

        node["completed"] = True
        node["completed_at"] = str(datetime.datetime.now())
        path.nodes_json = json.dumps(path_data, ensure_ascii=False)

        # Update profile: move topic from weak_points → mastered_topics
        node_title = node.get("title", "")
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        if profile and node_title:
            kb = profile.setdefault("knowledge_base", {})
            mastered = kb.get("mastered_topics", [])
            weak = kb.get("weak_points", [])

            if node_title in weak:
                weak.remove(node_title)
                kb["weak_points"] = weak

            if node_title not in mastered:
                mastered = list(mastered)
                mastered.append(node_title)
                kb["mastered_topics"] = mastered

            # Bump level if enough topics mastered
            if len(mastered) >= 8:
                kb["level"] = "advanced"
            elif len(mastered) >= 4:
                kb["level"] = "intermediate"

            self.profile_service._save_profile(db, student_id, profile)

        db.commit()
        return {"ok": True, "node_title": node_title, "profile_updated": profile is not None and bool(node_title)}

    def delete_path(self, db: Session, student_id: int, path_id: int) -> bool:
        """Delete a learning path by id."""
        path = (
            db.query(LearningPath)
            .filter(LearningPath.id == path_id, LearningPath.student_id == student_id)
            .first()
        )
        if not path:
            return False
        db.delete(path)
        db.commit()
        return True
