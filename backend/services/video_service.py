import json
from sqlalchemy.orm import Session
from backend.models.resource import LearningResource
from backend.agents.resource_agents.seedance_agent import SeedanceAgent


class VideoService:
    def __init__(self):
        self.agent = SeedanceAgent()

    def generate_video(self, db: Session, resource_id: int) -> dict:
        """Trigger video generation for an existing video_script resource."""
        resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
        if not resource:
            return {"success": False, "error": "Resource not found"}
        if resource.resource_type != "video_script":
            return {"success": False, "error": "Resource is not a video script"}

        # Call Seedance
        result = self.agent.generate(resource.content)

        # Save metadata
        meta = self._get_meta(resource)
        if result.get("success"):
            meta["seedance_task_id"] = result["task_id"]
            meta["seedance_status"] = "queued"
            meta["seedance_prompt"] = result.get("prompt_used", "")
        else:
            meta["seedance_status"] = "failed"
            meta["seedance_error"] = result.get("error", "")

        resource.metadata_json = json.dumps(meta, ensure_ascii=False)
        db.commit()

        return result

    def check_video_status(self, db: Session, resource_id: int) -> dict:
        """Check Seedance generation status and update metadata if completed."""
        resource = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
        if not resource:
            return {"success": False, "error": "Resource not found"}

        meta = self._get_meta(resource)
        task_id = meta.get("seedance_task_id")
        if not task_id:
            return {"success": False, "error": "No Seedance task found for this resource"}

        result = self.agent.check_status(task_id)

        # Update metadata with latest status
        meta["seedance_status"] = result.get("status", "unknown")
        if result.get("video_url"):
            meta["seedance_video_url"] = result["video_url"]
        if result.get("progress"):
            meta["seedance_progress"] = result["progress"]

        resource.metadata_json = json.dumps(meta, ensure_ascii=False)
        db.commit()

        return {"success": True, **result}

    @staticmethod
    def _get_meta(resource: LearningResource) -> dict:
        try:
            return json.loads(resource.metadata_json)
        except (json.JSONDecodeError, TypeError):
            return {}
