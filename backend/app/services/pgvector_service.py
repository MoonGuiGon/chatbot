"""
pgvector Service - PostgreSQL with vector extension
"""
from typing import List, Dict, Any, Optional
import logging
import json
from sqlalchemy import create_engine, text, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector

from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DocumentEmbedding(Base):
    """Document embedding model for pgvector"""
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Adjust dimension based on your embedding model
    metadata = Column(JSON)
    summary = Column(Text)  # Vision model generated summary
    screenshot_path = Column(String(500))  # Path to screenshot


class PgVectorService:
    """PostgreSQL with pgvector for document retrieval"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.use_mock = True

    def initialize(self, db_uri: Optional[str] = None):
        """Initialize pgvector connection"""
        try:
            uri = db_uri or settings.postgres_uri
            self.engine = create_engine(uri, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Create pgvector extension and tables
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()

            Base.metadata.create_all(bind=self.engine)
            self.use_mock = False
            logger.info("pgvector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pgvector: {e}")
            logger.info("pgvector features will use mock data")
            self.use_mock = True

    def search_similar(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search similar documents using cosine similarity"""
        if self.use_mock:
            return self._get_mock_documents(n_results)

        try:
            with self.SessionLocal() as session:
                # Use pgvector's cosine distance operator
                query = session.query(
                    DocumentEmbedding.id,
                    DocumentEmbedding.content,
                    DocumentEmbedding.metadata,
                    DocumentEmbedding.summary,
                    DocumentEmbedding.screenshot_path,
                    DocumentEmbedding.embedding.cosine_distance(query_embedding).label('distance')
                )

                # Apply metadata filter if provided
                if filter_metadata:
                    for key, value in filter_metadata.items():
                        query = query.filter(
                            DocumentEmbedding.metadata[key].astext == str(value)
                        )

                # Order by similarity and limit
                results = query.order_by('distance').limit(n_results).all()

                documents = []
                for result in results:
                    doc = {
                        'id': result.id,
                        'content': result.content,
                        'metadata': result.metadata or {},
                        'summary': result.summary,
                        'screenshot_path': result.screenshot_path,
                        'distance': float(result.distance)
                    }
                    documents.append(doc)

                return documents
        except Exception as e:
            logger.error(f"pgvector search error: {e}")
            return self._get_mock_documents(n_results)

    def add_document(
        self,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        summary: Optional[str] = None,
        screenshot_path: Optional[str] = None
    ) -> bool:
        """Add document with embedding to pgvector"""
        if self.use_mock:
            logger.info(f"Mock: Would add document with metadata: {metadata}")
            return True

        try:
            with self.SessionLocal() as session:
                doc = DocumentEmbedding(
                    content=content,
                    embedding=embedding,
                    metadata=metadata,
                    summary=summary,
                    screenshot_path=screenshot_path
                )
                session.add(doc)
                session.commit()
                logger.info(f"Added document to pgvector: {metadata.get('source', 'unknown')}")
                return True
        except Exception as e:
            logger.error(f"Error adding document to pgvector: {e}")
            return False

    def batch_add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> int:
        """Batch add documents for better performance"""
        if self.use_mock:
            logger.info(f"Mock: Would add {len(documents)} documents")
            return len(documents)

        try:
            with self.SessionLocal() as session:
                doc_objects = []
                for doc in documents:
                    doc_obj = DocumentEmbedding(
                        content=doc['content'],
                        embedding=doc['embedding'],
                        metadata=doc.get('metadata', {}),
                        summary=doc.get('summary'),
                        screenshot_path=doc.get('screenshot_path')
                    )
                    doc_objects.append(doc_obj)

                session.bulk_save_objects(doc_objects)
                session.commit()
                logger.info(f"Batch added {len(documents)} documents to pgvector")
                return len(documents)
        except Exception as e:
            logger.error(f"Error batch adding documents: {e}")
            return 0

    def _get_mock_documents(self, n_results: int) -> List[Dict[str, Any]]:
        """Return mock documents for testing"""
        mock_docs = [
            {
                'id': 1,
                'content': '반도체 장비 부품 관리 지침\n\n1. 부품 보관 방법\n- 습도 40-60% 유지\n- 온도 20-25도 유지\n- 직사광선 차단',
                'metadata': {
                    'source': '부품관리지침.pdf',
                    'page': 1,
                    'type': 'pdf',
                    'date': '2024-01-15'
                },
                'summary': 'Vision Model Summary: 부품 보관 환경 조건에 대한 상세 지침. 습도와 온도 관리 중요.',
                'screenshot_path': '/screenshots/doc1_page1.png',
                'distance': 0.15
            },
            {
                'id': 2,
                'content': '반도체 공정 부품 사양서\n\n부품명: 진공 펌프 밸브\n자재코드: MAT-001',
                'metadata': {
                    'source': '부품사양서_MAT001.docx',
                    'type': 'docx',
                    'material_id': 'MAT-001',
                    'date': '2024-02-20'
                },
                'summary': 'Vision Model Summary: MAT-001 진공 펌프 밸브의 기술 사양 문서. 작동 압력 및 재질 정보 포함.',
                'screenshot_path': '/screenshots/doc2.png',
                'distance': 0.22
            },
            {
                'id': 3,
                'content': '2024년 1분기 부품 구매 현황\n\n총 구매액: 5억원\n주요 구매 품목...',
                'metadata': {
                    'source': '2024Q1_구매현황.pptx',
                    'page': 3,
                    'type': 'pptx',
                    'date': '2024-03-31'
                },
                'summary': 'Vision Model Summary: 2024년 1분기 부품 구매 실적 요약. 차트와 그래프 포함.',
                'screenshot_path': '/screenshots/doc3_slide3.png',
                'distance': 0.28
            }
        ]

        return mock_docs[:n_results]


# Global instance
pgvector_service = PgVectorService()
