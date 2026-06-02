from backend.agents.base import BaseAgent
from backend.config import SEEDANCE_API_KEY, SEEDANCE_BASE_URL, SEEDANCE_MODEL
import httpx
import json
import logging

logger = logging.getLogger(__name__)

SEEDANCE_AGENT_PROMPT = """你是一位**视频脚本编译专家**。你将教学视频脚本转换为适合 Seedance 视频生成模型的英文视觉 prompt。

## 你的任务
给定一个教学视频脚本（包含分镜、画面描述、旁白等），提取出适合 AI 视频生成的核心视觉描述。

## 输出要求
输出一个简洁的英文 prompt，描述要生成的视频画面，要求：
1. 聚焦于视觉元素（场景、人物、动作、色彩、光线）
2. 长度控制在 200 字符以内
3. 使用英文
4. 风格关键词：cinematic, educational, clear visual hierarchy

直接输出 prompt 文本，不要额外解释。
末尾不要加任何参数（例如 --resolution, --duration, --watermark 等），这些参数由代码自动追加。"""


class SeedanceAgent(BaseAgent):
    """Doubao-Seedance 视频生成智能体 — 通过火山方舟 ARK API 调用。"""

    def __init__(self):
        super().__init__(name="SeedanceAgent", system_prompt=SEEDANCE_AGENT_PROMPT)

    def compile_prompt(self, script_content: str) -> str:
        """Convert a video script into a concise Seedance visual prompt (English only)."""
        prompt = f"将以下教学视频脚本转换为一段英文视觉 prompt（200字符以内），用于 AI 视频生成。只输出英文 prompt，不要加任何参数：\n\n{script_content[:2000]}"
        return self.chat(prompt, temperature=0.4).strip()

    def generate(self, script_content: str, duration: int = 5, resolution: str = "1080p") -> dict:
        """
        Submit a text-to-video task to Doubao-Seedance via Volcengine ARK.
        Returns {"success": bool, "task_id": "...", "prompt_used": "..."}
        """
        visual_prompt = self.compile_prompt(script_content)

        # Append Seedance CLI parameters to the prompt text
        full_prompt = f"{visual_prompt}  --resolution {resolution}  --duration {duration}  --camerafixed false  --watermark true"

        payload = {
            "model": SEEDANCE_MODEL,
            "content": [
                {
                    "type": "text",
                    "text": full_prompt,
                },
            ],
        }

        headers = {
            "Authorization": f"Bearer {SEEDANCE_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            url = f"{SEEDANCE_BASE_URL}/contents/generations/tasks"
            logger.info(f"[Seedance] POST {url}")
            response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
            data = response.json()
            logger.info(f"[Seedance] status={response.status_code}, body={json.dumps(data, ensure_ascii=False)[:500]}")

            if response.status_code == 200 and data.get("id"):
                return {
                    "success": True,
                    "task_id": data["id"],
                    "status": "queued",
                    "prompt_used": visual_prompt,
                }
            else:
                err_msg = data.get("error", {}).get("message", "") or data.get("message", "") or json.dumps(data, ensure_ascii=False)
                return {"success": False, "error": err_msg, "prompt_used": visual_prompt}
        except Exception as e:
            logger.error(f"[Seedance] generate error: {e}")
            return {"success": False, "error": str(e), "prompt_used": visual_prompt}

    def check_status(self, task_id: str) -> dict:
        """
        Poll the Doubao-Seedance task status.
        Returns {"status": "queued|running|succeeded|failed", "video_url": "...", "progress": 0-100}
        """
        headers = {"Authorization": f"Bearer {SEEDANCE_API_KEY}"}

        try:
            url = f"{SEEDANCE_BASE_URL}/contents/generations/tasks/{task_id}"
            response = httpx.get(url, headers=headers, timeout=30.0)
            data = response.json()

            if response.status_code == 200:
                status = data.get("status", "unknown")
                # content is an object: {"video_url": "https://..."} (not an array)
                content = data.get("content", {})
                video_url = content.get("video_url") if isinstance(content, dict) else None

                status_map = {
                    "succeeded": "completed",
                    "completed": "completed",
                    "running": "processing",
                    "processing": "processing",
                    "queued": "queued",
                    "failed": "failed",
                }
                return {
                    "status": status_map.get(status, status),
                    "video_url": video_url or data.get("video_url"),
                    "progress": data.get("progress", 0),
                }
            else:
                return {"status": "failed", "error": data.get("error", {}).get("message", response.text)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
