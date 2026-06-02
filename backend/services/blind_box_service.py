import random
import datetime
import logging
from sqlalchemy.orm import Session
from backend.services.profile_service import ProfileService
from backend.services.rag_service import rag_service
from backend.agents.blind_box_agent import BlindBoxAgent

logger = logging.getLogger(__name__)


class BlindBoxService:
    def __init__(self):
        self.profile_service = ProfileService()
        self.agent = BlindBoxAgent()

    def get_daily_card(self, db: Session, student_id: int) -> dict:
        """Return a daily knowledge card, personalized via AI agent + RAG."""
        profile_data = self.profile_service.get_profile(db, student_id)
        profile = profile_data["profile"] if profile_data else {}

        today = datetime.date.today()
        seed = today.toordinal() + student_id
        rng = random.Random(seed)

        rag_context = []
        if profile:
            kb = profile.get("knowledge_base", {})
            mf = profile.get("motivation_factors", {})
            search_terms = []
            for wp in kb.get("weak_points", [])[:3]:
                t = wp if isinstance(wp, str) else wp.get("topic", "")
                if t:
                    search_terms.append(t)
            goal = mf.get("primary_goal", "")
            if goal:
                search_terms.append(goal)
            interests = mf.get("interests", [])[:3]
            search_terms.extend([i for i in interests if isinstance(i, str)])

            if search_terms:
                query = " ".join(search_terms)
                try:
                    rag_context = rag_service.search(student_id, query, n_results=3)
                    if not rag_context:
                        rag_service.build_index(db, student_id)
                        rag_context = rag_service.search(student_id, query, n_results=3)
                except Exception as e:
                    logger.warning(f"RAG search failed: {e}")

        card = self.agent.generate_card(profile, rag_context)

        box_types = [
            {"icon": "🎁", "label": "知识盲盒"},
            {"icon": "🔮", "label": "今日预言"},
            {"icon": "💎", "label": "知识宝石"},
            {"icon": "🎯", "label": "每日一得"},
            {"icon": "🌟", "label": "今日新知"},
        ]
        box = rng.choice(box_types)

        result = {
            "date": today.isoformat(),
            "box_icon": box["icon"],
            "box_label": box["label"],
            "title": card["title"],
            "content": card["content"],
            "category": card["category"],
            "difficulty": card["difficulty"],
        }

        # Index into RAG so future blind boxes can learn from past ones
        try:
            rag_service.index_blind_box(student_id, result)
        except Exception as e:
            logger.warning(f"Failed to index blind box: {e}")

        return result
