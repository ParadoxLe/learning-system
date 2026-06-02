import os
import logging
from sqlalchemy.orm import Session
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from backend.models.resource import LearningResource
from backend.models.uploaded_file import UploadedFile

logger = logging.getLogger(__name__)

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")


class RAGService:
    def __init__(self):
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = DashScopeEmbeddings(
                model="text-embedding-v1",
            )
        return self._embeddings

    def _get_store(self, student_id: int) -> Chroma:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        return Chroma(
            collection_name=f"student_{student_id}",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PATH,
        )

    def _chunk_text(self, text: str, size: int = 500) -> list[str]:
        return [text[i:i+size] for i in range(0, len(text), size)]

    def index_resources(self, db: Session, student_id: int) -> int:
        resources = db.query(LearningResource).filter(
            LearningResource.student_id == student_id
        ).all()
        if not resources:
            return 0

        store = self._get_store(student_id)
        ids, docs, metas = [], [], []

        for r in resources:
            content = r.content or ""
            full_text = f"{r.title or ''}\n{content}"
            chunks = self._chunk_text(full_text)
            for ci, chunk in enumerate(chunks):
                chunk_id = f"res_{r.id}_{ci}"
                ids.append(chunk_id)
                docs.append(chunk)
                metas.append({
                    "source": "resource",
                    "resource_id": r.id,
                    "title": r.title or "",
                    "resource_type": r.resource_type or "",
                })

        if ids:
            store.add_texts(texts=docs, ids=ids, metadatas=metas)
        logger.info(f"Indexed {len(ids)} resource chunks for student {student_id}")
        return len(ids)

    def index_uploaded_files(self, db: Session, student_id: int) -> int:
        files = db.query(UploadedFile).filter(
            UploadedFile.student_id == student_id
        ).all()
        if not files:
            return 0

        store = self._get_store(student_id)
        ids, docs, metas = [], [], []

        for f in files:
            text = f.content_text or ""
            if not text.strip():
                continue
            chunks = self._chunk_text(text)
            for ci, chunk in enumerate(chunks):
                chunk_id = f"file_{f.id}_{ci}"
                ids.append(chunk_id)
                docs.append(chunk)
                metas.append({
                    "source": "uploaded_file",
                    "file_id": f.id,
                    "filename": f.original_name or f.filename or "",
                })

        if ids:
            store.add_texts(texts=docs, ids=ids, metadatas=metas)
        logger.info(f"Indexed {len(ids)} file chunks for student {student_id}")
        return len(ids)

    def build_index(self, db: Session, student_id: int) -> dict:
        n_res = self.index_resources(db, student_id)
        n_file = self.index_uploaded_files(db, student_id)
        return {"resources_chunks": n_res, "files_chunks": n_file}

    def search(self, student_id: int, query: str, n_results: int = 3) -> list[str]:
        try:
            store = self._get_store(student_id)
            docs = store.similarity_search(query, k=n_results)
            return [d.page_content for d in docs if d.page_content]
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")
            return []

    def index_blind_box(self, student_id: int, card: dict):
        """Index a blind box card into the RAG store."""
        store = self._get_store(student_id)
        text = f"{card['title']}\n{card['content']}"
        store.add_texts(
            texts=[text],
            ids=[f"blindbox_{card.get('date', '')}_{card.get('title', '')[:20]}"],
            metadatas=[{
                "source": "blind_box",
                "category": card.get("category", ""),
                "difficulty": card.get("difficulty", ""),
                "date": card.get("date", ""),
            }],
        )
        logger.info(f"Indexed blind box card for student {student_id}")

    def delete_student_index(self, student_id: int):
        try:
            store = self._get_store(student_id)
            store.delete_collection()
        except Exception:
            pass


rag_service = RAGService()
