"""
테스트용 Mock Database
실제 MongoDB, pgvector 없이도 개발 및 테스트 가능
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np


class MockMongoDB:
    """Mock MongoDB - 부품 정보 저장"""

    def __init__(self):
        self.data = {
            "parts": self._init_parts_data(),
            "conversations": [],
            "feedback": [],
            "document_metadata": []
        }

    def _init_parts_data(self) -> List[Dict[str, Any]]:
        """초기 부품 데이터"""
        return [
            {
                "_id": "part_001",
                "part_number": "ABC-12345",
                "part_name": "반도체 칩 A",
                "category": "IC",
                "inventory": {
                    "total_stock": 1000,
                    "available": 850,
                    "reserved": 150,
                    "last_updated": datetime.now().isoformat()
                },
                "shipment_history": [
                    {
                        "date": (datetime.now() - timedelta(days=5)).isoformat(),
                        "quantity": 100,
                        "destination": "라인 1"
                    },
                    {
                        "date": (datetime.now() - timedelta(days=10)).isoformat(),
                        "quantity": 50,
                        "destination": "라인 2"
                    }
                ],
                "installation_records": [
                    {
                        "equipment_id": "EQ-001",
                        "installed_date": (datetime.now() - timedelta(days=30)).isoformat(),
                        "status": "active"
                    },
                    {
                        "equipment_id": "EQ-002",
                        "installed_date": (datetime.now() - timedelta(days=20)).isoformat(),
                        "status": "active"
                    }
                ],
                "inspection_data": [
                    {
                        "inspection_date": (datetime.now() - timedelta(days=2)).isoformat(),
                        "parameters": {
                            "voltage": 3.3,
                            "current": 0.5,
                            "temperature": 25
                        },
                        "result": "pass"
                    }
                ],
                "metadata": {
                    "supplier": "Supplier A",
                    "created_at": (datetime.now() - timedelta(days=365)).isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            },
            {
                "_id": "part_002",
                "part_number": "ABC-12346",
                "part_name": "반도체 칩 B",
                "category": "IC",
                "inventory": {
                    "total_stock": 500,
                    "available": 450,
                    "reserved": 50,
                    "last_updated": datetime.now().isoformat()
                },
                "shipment_history": [
                    {
                        "date": (datetime.now() - timedelta(days=3)).isoformat(),
                        "quantity": 30,
                        "destination": "라인 3"
                    }
                ],
                "installation_records": [
                    {
                        "equipment_id": "EQ-003",
                        "installed_date": (datetime.now() - timedelta(days=15)).isoformat(),
                        "status": "active"
                    }
                ],
                "inspection_data": [
                    {
                        "inspection_date": (datetime.now() - timedelta(days=1)).isoformat(),
                        "parameters": {
                            "voltage": 5.0,
                            "current": 0.8,
                            "temperature": 28
                        },
                        "result": "pass"
                    }
                ],
                "metadata": {
                    "supplier": "Supplier B",
                    "created_at": (datetime.now() - timedelta(days=200)).isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            },
            {
                "_id": "part_003",
                "part_number": "ABC-12347",
                "part_name": "반도체 칩 C",
                "category": "IC",
                "inventory": {
                    "total_stock": 200,
                    "available": 50,
                    "reserved": 150,
                    "last_updated": datetime.now().isoformat()
                },
                "shipment_history": [
                    {
                        "date": (datetime.now() - timedelta(days=1)).isoformat(),
                        "quantity": 150,
                        "destination": "라인 1"
                    }
                ],
                "installation_records": [
                    {
                        "equipment_id": "EQ-001",
                        "installed_date": (datetime.now() - timedelta(days=5)).isoformat(),
                        "status": "active"
                    }
                ],
                "inspection_data": [
                    {
                        "inspection_date": datetime.now().isoformat(),
                        "parameters": {
                            "voltage": 3.3,
                            "current": 0.6,
                            "temperature": 30
                        },
                        "result": "pass"
                    }
                ],
                "metadata": {
                    "supplier": "Supplier A",
                    "created_at": (datetime.now() - timedelta(days=100)).isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            }
        ]

    def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """문서 검색"""
        if collection not in self.data:
            return []

        results = []
        for doc in self.data[collection]:
            if self._match_query(doc, query):
                results.append(doc)

        return results

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """단일 문서 검색"""
        results = self.find(collection, query)
        return results[0] if results else None

    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """문서 추가"""
        if collection not in self.data:
            self.data[collection] = []

        doc_id = f"{collection}_{len(self.data[collection]) + 1}"
        document["_id"] = doc_id
        self.data[collection].append(document)
        return doc_id

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """문서 업데이트"""
        if collection not in self.data:
            return False

        for doc in self.data[collection]:
            if self._match_query(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])
                return True

        return False

    def _match_query(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """쿼리 매칭"""
        for key, value in query.items():
            if key not in doc:
                return False
            if doc[key] != value:
                return False
        return True


class MockPgVector:
    """Mock pgvector - 문서 벡터 저장"""

    def __init__(self):
        self.documents = self._init_document_chunks()
        self.images = []

    def _init_document_chunks(self) -> List[Dict[str, Any]]:
        """초기 문서 청크 데이터"""
        return [
            {
                "id": 1,
                "document_id": "doc_001",
                "chunk_index": 0,
                "content": """
반도체 칩 ABC-12345 사양서

1. 기본 사양
- 동작 전압: 3.3V ± 0.3V
- 소비 전류: 최대 0.5A
- 동작 온도 범위: -40°C ~ 85°C
- 패키지: QFN-48

2. 핀 배치
- VDD: 1, 12, 24, 36
- GND: 13, 25, 37, 48
- I/O: 2-11, 14-23, 26-35, 38-47
""",
                "chunk_type": "text",
                "embedding": np.random.rand(1536).tolist(),
                "metadata": {
                    "file_name": "부품_매뉴얼_ABC12345.pdf",
                    "page_number": 1,
                    "section": "사양",
                    "category": "반도체",
                    "keywords": ["사양", "전압", "전류", "온도"]
                }
            },
            {
                "id": 2,
                "document_id": "doc_001",
                "chunk_index": 1,
                "content": """
3. 전기적 특성
- 입력 전압 범위: 3.0V ~ 3.6V
- 출력 전압: 3.3V
- 리플 전압: 50mV 이하
- 효율: 90% 이상

4. 보관 조건
- 온도: -55°C ~ 150°C
- 습도: 상대습도 85% 이하
- 정전기 주의: ESD 민감 부품
""",
                "chunk_type": "text",
                "embedding": np.random.rand(1536).tolist(),
                "metadata": {
                    "file_name": "부품_매뉴얼_ABC12345.pdf",
                    "page_number": 2,
                    "section": "전기적 특성",
                    "category": "반도체",
                    "keywords": ["전압", "효율", "보관"]
                }
            },
            {
                "id": 3,
                "document_id": "doc_002",
                "chunk_index": 0,
                "content": """
반도체 부품 재고 관리 지침

1. 재고 확인 주기
- 일반 부품: 주 1회
- 중요 부품: 매일
- 긴급 부품: 실시간 모니터링

2. 최소 재고 기준
- A급 부품: 1000개 이상
- B급 부품: 500개 이상
- C급 부품: 200개 이상

3. 발주 기준
- 가용 재고가 최소 재고의 50% 이하로 떨어지면 자동 발주
""",
                "chunk_type": "text",
                "embedding": np.random.rand(1536).tolist(),
                "metadata": {
                    "file_name": "재고_관리_지침.docx",
                    "page_number": 1,
                    "section": "재고 관리",
                    "category": "운영",
                    "keywords": ["재고", "발주", "관리"]
                }
            },
            {
                "id": 4,
                "document_id": "doc_003",
                "chunk_index": 0,
                "content": """
부품 입고 검사 절차

1. 외관 검사
- 포장 상태 확인
- 라벨 정보 확인
- 수량 확인

2. 전기적 검사
- 전압 측정
- 전류 측정
- 저항 측정

3. 기능 검사
- 동작 테스트
- 성능 테스트

검사 결과는 시스템에 즉시 등록해야 합니다.
""",
                "chunk_type": "text",
                "embedding": np.random.rand(1536).tolist(),
                "metadata": {
                    "file_name": "검사_절차.pdf",
                    "page_number": 1,
                    "section": "검사",
                    "category": "품질",
                    "keywords": ["검사", "입고", "품질"]
                }
            }
        ]

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """벡터 유사도 검색 (Mock)"""

        # 필터링
        candidates = self.documents
        if filter_metadata:
            candidates = [
                doc for doc in self.documents
                if all(
                    doc["metadata"].get(key) == value
                    for key, value in filter_metadata.items()
                )
            ]

        # 유사도 계산 (코사인 유사도)
        query_vec = np.array(query_embedding)
        similarities = []

        for doc in candidates:
            doc_vec = np.array(doc["embedding"])
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
            )
            similarities.append((doc, float(similarity)))

        # 상위 k개 반환
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [
            {**doc, "similarity_score": score}
            for doc, score in similarities[:k]
        ]

        return results

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[int]:
        """문서 추가"""
        ids = []
        for doc in documents:
            doc_id = len(self.documents) + 1
            doc["id"] = doc_id
            self.documents.append(doc)
            ids.append(doc_id)
        return ids

    def delete_document(self, document_id: str) -> bool:
        """문서 삭제"""
        self.documents = [
            doc for doc in self.documents
            if doc["document_id"] != document_id
        ]
        return True


class MockDatabaseFactory:
    """Mock Database 팩토리 - 테스트 모드에서 사용"""

    _mongodb_instance = None
    _pgvector_instance = None

    @classmethod
    def get_mongodb(cls) -> MockMongoDB:
        """MongoDB 인스턴스 반환 (싱글톤)"""
        if cls._mongodb_instance is None:
            cls._mongodb_instance = MockMongoDB()
        return cls._mongodb_instance

    @classmethod
    def get_pgvector(cls) -> MockPgVector:
        """pgvector 인스턴스 반환 (싱글톤)"""
        if cls._pgvector_instance is None:
            cls._pgvector_instance = MockPgVector()
        return cls._pgvector_instance

    @classmethod
    def reset(cls):
        """모든 데이터 초기화"""
        cls._mongodb_instance = None
        cls._pgvector_instance = None
