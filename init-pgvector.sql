-- pgvector 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 문서 테이블 생성
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 벡터 유사도 검색을 위한 인덱스 생성
-- IVFFlat 인덱스: 빠른 검색을 위한 근사 최근접 이웃 인덱스
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 메타데이터 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS documents_metadata_idx
ON documents USING gin (metadata);

-- 전체 텍스트 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS documents_content_idx
ON documents USING gin (to_tsvector('english', content));

-- 테이블 정보 출력
\d documents

-- 확인 메시지
SELECT 'pgvector 초기화 완료!' as status;
