import os
import uuid
from sqlalchemy.orm import Session
from backend.models.uploaded_file import UploadedFile
from backend.agents.base import BaseAgent

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "uploads")

EXPLAIN_PROMPT = """你是一位**知识讲解助手**。用户从PDF文档中选中了一段文字，请你用通俗易懂的语言解释这段内容。

## 要求
1. 先用一两句话概括这段文字的核心意思
2. 然后逐点详细解释关键概念
3. 如果涉及专业术语，给出定义
4. 最后给出一个简单的例子帮助理解
5. 用 Markdown 格式输出，结构清晰"""


class LibraryService:
    def __init__(self):
        self.explain_agent = BaseAgent(name="ExplainAgent", system_prompt=EXPLAIN_PROMPT)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def upload_pdf(self, db: Session, student_id: int, filename: str, file_content: bytes) -> dict:
        """Save uploaded PDF, extract text, store record."""
        safe_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Extract text
        text = ""
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            text = "[无法解析PDF文本]"

        record = UploadedFile(
            student_id=student_id,
            filename=safe_name,
            original_name=filename,
            file_path=file_path,
            content_text=text[:50000],  # limit text length
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "filename": record.original_name,
            "text_preview": text[:300],
            "text_length": len(text),
            "created_at": str(record.created_at),
        }

    def list_files(self, db: Session, student_id: int) -> list[dict]:
        """List all uploaded files for a student."""
        records = (
            db.query(UploadedFile)
            .filter(UploadedFile.student_id == student_id)
            .order_by(UploadedFile.created_at.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "filename": r.original_name,
                "text_length": len(r.content_text),
                "created_at": str(r.created_at),
            }
            for r in records
        ]

    def get_file(self, db: Session, student_id: int, file_id: int):  # -> dict | None (Python 3.10+)
        """Get file info with extracted text."""
        record = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == file_id, UploadedFile.student_id == student_id)
            .first()
        )
        if not record:
            return None
        return {
            "id": record.id,
            "filename": record.original_name,
            "file_path": record.file_path,
            "content_text": record.content_text,
            "created_at": str(record.created_at),
        }

    def delete_file(self, db: Session, student_id: int, file_id: int) -> bool:
        """Delete an uploaded file record and the file on disk."""
        record = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == file_id, UploadedFile.student_id == student_id)
            .first()
        )
        if not record:
            return False
        if os.path.exists(record.file_path):
            os.remove(record.file_path)
        db.delete(record)
        db.commit()
        return True

    def explain_text(self, selected_text: str, context: str = "") -> str:
        """Ask AI to explain the selected text."""
        prompt = f"""上下文（来自PDF文档）：
{context[:1000]}

用户选中的文字：
{selected_text}

请解释这段选中的文字。"""
        return self.explain_agent.chat(prompt, temperature=0.5)
