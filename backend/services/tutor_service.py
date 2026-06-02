import json
from sqlalchemy.orm import Session
from backend.agents.tutor_agent import TutorAgent
from backend.agents.assessment_agent import AssessmentAgent
from backend.services.profile_service import ProfileService


class TutorService:
    def __init__(self):
        self.tutor_agent = TutorAgent()
        self.assessment_agent = AssessmentAgent()
        self.profile_service = ProfileService()

    def answer_question(self, db: Session, student_id: int, question: str, context: str = "") -> str:
        """Answer a student's question with personalized tutoring."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}
        return self.tutor_agent.answer(question, profile, context)

    def answer_question_stream(self, db: Session, student_id: int, question: str, context: str = ""):
        """Stream a personalized answer token by token."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}
        yield from self.tutor_agent.answer_stream(question, profile, context)

    def evaluate(self, db: Session, student_id: int, learning_data: dict) -> dict:
        """Evaluate student learning effectiveness and auto-update profile."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}
        result = self.assessment_agent.evaluate(profile, learning_data)

        # Auto-update profile based on assessment results
        if profile and result and "dimensions" in result:
            self._auto_update_profile(db, student_id, profile, result)

        return result

    def _auto_update_profile(self, db: Session, student_id: int, profile: dict, assessment: dict):
        """Incrementally update profile dimensions from assessment results."""
        dims = assessment.get("dimensions", {})

        # Update weak_points from assessment
        weak_points_data = dims.get("weak_points", [])
        if weak_points_data:
            existing_weak = set(profile.get("knowledge_base", {}).get("weak_points", []))
            for wp in weak_points_data:
                topic = wp.get("topic", "")
                if topic and topic not in existing_weak:
                    existing_weak.add(topic)
            profile.setdefault("knowledge_base", {})["weak_points"] = list(existing_weak)

        # Update level based on overall score
        overall = assessment.get("overall_score", 0)
        if overall > 0:
            kb = profile.setdefault("knowledge_base", {})
            if overall >= 80:
                kb["level"] = "advanced"
            elif overall >= 50:
                kb["level"] = "intermediate"
            else:
                kb["level"] = "beginner"

        # Update error patterns
        if weak_points_data:
            ep = profile.setdefault("error_patterns", {})
            patterns = list(ep.get("patterns", [])) if isinstance(ep, dict) else []
            existing_topics = {p.get("topic", "") for p in patterns}
            for wp in weak_points_data:
                topic = wp.get("topic", "")
                if topic and topic not in existing_topics:
                    patterns.append({
                        "topic": topic,
                        "error_type": "概念混淆",
                        "frequency": wp.get("severity", "medium"),
                    })
            if isinstance(ep, dict):
                ep["patterns"] = patterns
            else:
                profile["error_patterns"] = patterns

        # Update learning pace efficiency
        efficiency = dims.get("efficiency", {})
        if efficiency.get("score", 0) > 0:
            lp = profile.setdefault("learning_pace", {})
            eff_score = efficiency.get("score", 65)
            if eff_score >= 80:
                lp["speed"] = "fast"
            elif eff_score >= 50:
                lp["speed"] = "moderate"
            else:
                lp["speed"] = "slow_and_deep"

        self.profile_service._save_profile(db, student_id, profile)
