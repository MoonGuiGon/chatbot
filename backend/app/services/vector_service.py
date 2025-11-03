"""
Vector Database Service
"""
from typing import List, Dict, Any, Optional
import logging
import json
import os

logger = logging.getLogger(__name__)


class VectorDBService:
    """Vector Database Service for document retrieval"""

    def __init__(self):
        self.client = None
        self.collection = None
        self.use_mock = True

    def initialize(self, collection_name: str = "documents"):
        """Initialize vector database"""
        try:
            import chromadb
            from app.config import settings

            self.client = chromadb.PersistentClient(path=settings.vectordb_path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            self.use_mock = False
            logger.info(f"VectorDB initialized with collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorDB: {e}")
            logger.info("VectorDB features will use mock data")
            self.use_mock = True

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search similar documents"""
        if self.use_mock:
            return self._get_mock_documents(query, n_results)

        try:
            from app.services.llm_service import llm_service

            # Get query embedding
            query_embedding = llm_service.get_embedding(query)
            if not query_embedding:
                return self._get_mock_documents(query, n_results)

            # Search in vector DB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )

            documents = []
            if results and 'documents' in results and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    doc = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                        'distance': results['distances'][0][i] if 'distances' in results else 0
                    }
                    documents.append(doc)

            return documents
        except Exception as e:
            logger.error(f"VectorDB search error: {e}")
            return self._get_mock_documents(query, n_results)

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """Add documents to vector DB"""
        if self.use_mock:
            logger.info(f"Mock: Would add {len(documents)} documents")
            return True

        try:
            from app.services.llm_service import llm_service

            # Get embeddings
            embeddings = []
            for doc in documents:
                emb = llm_service.get_embedding(doc)
                if emb:
                    embeddings.append(emb)
                else:
                    return False

            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"Added {len(documents)} documents to VectorDB")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def _get_mock_documents(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Return mock documents for testing"""
        mock_docs = [
            {
                'content': '반도체 장비 부품 관리 지침\n\n1. 부품 보관 방법\n- 습도 40-60% 유지\n- 온도 20-25도 유지\n- 직사광선 차단\n\n2. 재고 관리\n- 최소 재고량: 각 부품당 50개\n- 주간 재고 점검 필수\n- 재고 부족시 즉시 발주',
                'metadata': {
                    'source': '부품관리지침.pdf',
                    'page': 1,
                    'type': 'pdf',
                    'date': '2024-01-15'
                },
                'distance': 0.15
            },
            {
                'content': '반도체 공정 부품 사양서\n\n부품명: 진공 펌프 밸브\n자재코드: MAT-001\n\n주요 사양:\n- 작동 압력: 1-10 Torr\n- 재질: 스테인리스 스틸 316L\n- 수명: 10,000 사이클\n\n점검 주기: 3개월마다 정기 점검',
                'metadata': {
                    'source': '부품사양서_MAT001.docx',
                    'type': 'docx',
                    'material_id': 'MAT-001',
                    'date': '2024-02-20'
                },
                'distance': 0.22
            },
            {
                'content': '2024년 1분기 부품 구매 현황\n\n총 구매액: 5억원\n주요 구매 품목:\n1. 진공 펌프 부품 - 1.5억원\n2. 전자 밸브 - 1.2억원\n3. 센서류 - 8천만원\n\n공급업체별 구매 현황은 첨부 엑셀 파일 참조',
                'metadata': {
                    'source': '2024Q1_구매현황.pptx',
                    'page': 3,
                    'type': 'pptx',
                    'date': '2024-03-31'
                },
                'distance': 0.28
            },
            {
                'content': '장비 라인별 부품 장착 이력\n\n라인 1 (EQ-001):\n- 2024-03-10: MAT-001 교체 (진공 펌프 밸브)\n- 2024-03-15: MAT-045 신규 장착 (압력 센서)\n\n라인 2 (EQ-002):\n- 2024-03-20: MAT-001 교체\n- 2024-03-22: MAT-033 정기 점검',
                'metadata': {
                    'source': '장착이력_2024_03.xlsx',
                    'sheet': '라인별이력',
                    'type': 'xlsx',
                    'date': '2024-03-31'
                },
                'distance': 0.35
            },
            {
                'content': '반도체 부품 품질 관리 기준\n\n검사 항목:\n1. 외관 검사 - 스크래치, 오염 확인\n2. 치수 검사 - 공차 ±0.01mm\n3. 기능 검사 - 작동 테스트\n\n불량 판정 기준:\n- 외관 불량: 1mm 이상 스크래치\n- 치수 불량: 공차 초과\n- 기능 불량: 작동 불가',
                'metadata': {
                    'source': '품질관리기준.pdf',
                    'page': 5,
                    'type': 'pdf',
                    'date': '2024-01-10'
                },
                'distance': 0.42
            }
        ]

        return mock_docs[:n_results]


# Global instance
vector_service = VectorDBService()
