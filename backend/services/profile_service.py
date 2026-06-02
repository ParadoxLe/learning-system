import json
from sqlalchemy.orm import Session
from backend.models.student import Student
from backend.models.profile import LearningProfile
from backend.agents.profile_agent import ProfileAgent

# Store conversation history in memory (simplified; for production use Redis or DB)
_conversation_store: dict[int, list[dict]] = {}


class ProfileService:
    def __init__(self):
        self.agent = ProfileAgent()

    def chat(self, db: Session, student_id: int, message: str) -> dict:
        """Handle one round of profile-building conversation."""
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {"status": "error", "message": f"学生 {student_id} 不存在，请先创建学生"}

        # Get conversation history
        history = _conversation_store.get(student_id, [])

        # Call agent
        result = self.agent.build_profile(message, history)

        # Save to history
        history.append({"role": "user", "content": message})
        if result["status"] == "need_more_info":
            history.append({"role": "assistant", "content": result["message"]})
        else:
            history.append({"role": "assistant", "content": json.dumps(result["profile"], ensure_ascii=False)})
        _conversation_store[student_id] = history

        # If profile complete, save to DB
        if result["status"] == "complete":
            self._save_profile(db, student_id, result["profile"])

        return result

    def chat_stream(self, db: Session, student_id: int, message: str):
        """Streaming profile chat — streams tokens only for follow-up questions, not for JSON profile."""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            yield {"status": "error", "message": f"学生 {student_id} 不存在"}
            return

        history = _conversation_store.get(student_id, [])
        tokens = []
        full_text = ""
        final_result = None

        for item in self.agent.build_profile_stream(message, history):
            if isinstance(item, dict):
                final_result = item
            else:
                tokens.append(item)
                full_text += item

        if final_result is None:
            final_result = {"status": "need_more_info", "message": full_text}

        # Save to history
        history.append({"role": "user", "content": message})
        if final_result["status"] == "need_more_info":
            history.append({"role": "assistant", "content": final_result.get("message", "")})
        else:
            history.append({"role": "assistant", "content": json.dumps(final_result.get("profile", {}), ensure_ascii=False)})
        _conversation_store[student_id] = history

        if final_result["status"] == "complete":
            self._save_profile(db, student_id, final_result["profile"])
            yield final_result
        else:
            # Replay buffered tokens for follow-up questions (streaming feel)
            for token in tokens:
                yield token
            yield final_result

    async def chat_stream_async(self, db: Session, student_id: int, message: str):
        """Async streaming profile chat — streams tokens only for follow-up questions, not for JSON profile."""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            yield {"status": "error", "message": f"学生 {student_id} 不存在"}
            return

        history = _conversation_store.get(student_id, [])
        tokens = []
        full_text = ""
        final_result = None

        async for item in self.agent.build_profile_stream_async(message, history):
            if isinstance(item, dict):
                final_result = item
            else:
                tokens.append(item)
                full_text += item

        if final_result is None:
            final_result = {"status": "need_more_info", "message": full_text}

        # Save to history
        history.append({"role": "user", "content": message})
        if final_result["status"] == "need_more_info":
            history.append({"role": "assistant", "content": final_result.get("message", "")})
        else:
            history.append({"role": "assistant", "content": json.dumps(final_result.get("profile", {}), ensure_ascii=False)})
        _conversation_store[student_id] = history

        if final_result["status"] == "complete":
            self._save_profile(db, student_id, final_result["profile"])
            yield final_result
        else:
            for token in tokens:
                yield token
            yield final_result

    def get_profile(self, db: Session, student_id: int):  # -> dict | None (Python 3.10+)
        """Get the latest profile for a student."""
        profile = (
            db.query(LearningProfile)
            .filter(LearningProfile.student_id == student_id)
            .order_by(LearningProfile.version.desc())
            .first()
        )
        if profile:
            return {
                "student_id": student_id,
                "profile": json.loads(profile.profile_json),
                "version": profile.version,
            }
        return None

    def update_profile(self, db: Session, student_id: int, new_info: str) -> dict:
        """Update existing profile with new information."""
        existing = self.get_profile(db, student_id)
        if not existing:
            return {"status": "error", "message": "No existing profile found"}

        updated = self.agent.update_profile(existing["profile"], new_info)
        self._save_profile(db, student_id, updated)
        return {"status": "complete", "profile": updated}

    def _save_profile(self, db: Session, student_id: int, profile_data: dict):
        """Save or update profile in database."""
        existing = (
            db.query(LearningProfile)
            .filter(LearningProfile.student_id == student_id)
            .order_by(LearningProfile.version.desc())
            .first()
        )

        if existing:
            existing.profile_json = json.dumps(profile_data, ensure_ascii=False)
            existing.version += 1
        else:
            new_profile = LearningProfile(
                student_id=student_id,
                profile_json=json.dumps(profile_data, ensure_ascii=False),
                version=1,
            )
            db.add(new_profile)

        db.commit()
