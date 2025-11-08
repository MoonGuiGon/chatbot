"""
데이터베이스 서비스
MongoDB (부품 정보) 및 pgvector (문서 벡터) 연동
"""
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from app.config import config


class MongoDBService:
    """실제 MongoDB 서비스"""

    def __init__(self):
        self.client = MongoClient(config.database.mongodb_uri)
        self.db = self.client[config.database.mongodb_database]

    def find(self, collection: str, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """문서 검색"""
        return list(self.db[collection].find(query).limit(limit))

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """단일 문서 검색"""
        return self.db[collection].find_one(query)

    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """문서 추가"""
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """여러 문서 추가"""
        result = self.db[collection].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """문서 업데이트"""
        result = self.db[collection].update_one(query, update)
        return result.modified_count > 0

    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """문서 삭제"""
        result = self.db[collection].delete_one(query)
        return result.deleted_count > 0

    def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregation 쿼리"""
        return list(self.db[collection].aggregate(pipeline))


class PgVectorService:
    """실제 pgvector 서비스"""

    def __init__(self):
        self.conn = psycopg2.connect(config.database.postgres_uri)
        self._ensure_tables()

    def _ensure_tables(self):
        """테이블 생성 (없을 경우)"""
        with self.conn.cursor() as cur:
            # pgvector extension 활성화
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # document_chunks 테이블
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    chunk_type VARCHAR(50),
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # 인덱스 생성
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
                ON document_chunks USING hnsw (embedding vector_cosine_ops);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
                ON document_chunks (document_id);
            """)

            # image_embeddings 테이블
            cur.execute("""
                CREATE TABLE IF NOT EXISTS image_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_id VARCHAR(255) NOT NULL,
                    chunk_id INTEGER REFERENCES document_chunks(id),
                    image_path TEXT,
                    image_description TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            self.conn.commit()

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """벡터 유사도 검색"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT
                    id, document_id, chunk_index, content, chunk_type, metadata,
                    1 - (embedding <=> %s::vector) as similarity_score
                FROM document_chunks
            """

            params = [query_embedding]

            if filter_metadata:
                # metadata 필터 추가
                conditions = []
                for key, value in filter_metadata.items():
                    conditions.append(f"metadata->>'{key}' = %s")
                    params.append(str(value))

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY embedding <=> %s::vector LIMIT %s"
            params.extend([query_embedding, k])

            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[int]:
        """문서 추가"""
        with self.conn.cursor() as cur:
            query = """
                INSERT INTO document_chunks
                (document_id, chunk_index, content, chunk_type, embedding, metadata)
                VALUES %s
                RETURNING id
            """

            values = [
                (
                    doc["document_id"],
                    doc["chunk_index"],
                    doc["content"],
                    doc.get("chunk_type", "text"),
                    doc["embedding"],
                    doc.get("metadata")
                )
                for doc in documents
            ]

            ids = execute_values(cur, query, values, fetch=True)
            self.conn.commit()
            return [row[0] for row in ids]

    def delete_document(self, document_id: str) -> bool:
        """문서 삭제"""
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM document_chunks WHERE document_id = %s",
                (document_id,)
            )
            self.conn.commit()
            return cur.rowcount > 0


class DatabaseFactory:
    """
    Database 팩토리
    테스트 모드에 따라 Mock 또는 실제 DB 반환
    """

    @staticmethod
    def get_mongodb():
        """MongoDB 인스턴스 반환"""
        if config.test_mode:
            # 테스트 모드: Mock DB 사용
            from tests.mocks import MockDatabaseFactory
            return MockDatabaseFactory.get_mongodb()

        # 실제 모드: MongoDB 사용
        return MongoDBService()

    @staticmethod
    def get_pgvector():
        """pgvector 인스턴스 반환"""
        if config.test_mode:
            # 테스트 모드: Mock DB 사용
            from tests.mocks import MockDatabaseFactory
            return MockDatabaseFactory.get_pgvector()

        # 실제 모드: pgvector 사용
        return PgVectorService()


# 전역 DB 인스턴스
_mongodb = None
_pgvector = None


def get_mongodb():
    """MongoDB 인스턴스 반환"""
    global _mongodb
    if _mongodb is None:
        _mongodb = DatabaseFactory.get_mongodb()
    return _mongodb


def get_pgvector():
    """pgvector 인스턴스 반환"""
    global _pgvector
    if _pgvector is None:
        _pgvector = DatabaseFactory.get_pgvector()
    return _pgvector
