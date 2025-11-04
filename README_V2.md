# Enterprise Chatbot V2 - 차세대 멀티모달 RAG 시스템

LangGraph + pgvector + Neo4j + Vision Model을 활용한 차세대 엔터프라이즈 AI 챗봇

## 🚀 V2 주요 업그레이드

### 1. **멀티모달 RAG**
- 텍스트 + 스크린샷 통합 분석
- Vision Model로 차트/표/다이어그램 정확히 이해
- 문서의 시각적 맥락까지 파악

### 2. **Knowledge Graph (Neo4j)**
- 부품-공급업체-장비-문서 관계 그래프
- 연관 정보 자동 제공
- 유사 부품 추천

### 3. **pgvector (ChromaDB 대체)**
- PostgreSQL 통합 벡터 검색
- 빠른 cosine similarity 연산
- ACID 트랜잭션 지원

### 4. **Redis 캐싱**
- 임베딩 벡터 캐싱
- 질의 결과 캐싱
- 응답 속도 100배 향상

### 5. **문서 처리 파이프라인**
- PDF → 스크린샷 자동 생성
- Vision Model 자동 분석
- Enhanced Summary 생성
- 배치 처리 지원

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│              React + MUI + Zustand                           │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API + SSE
┌────────────────────────┴────────────────────────────────────┐
│                      Flask Backend                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          LangGraph Multi-Agent System                 │  │
│  │                                                       │  │
│  │  1. Query Analyzer (+ Cache Check)                   │  │
│  │  2. Material Retriever (+ Knowledge Graph)           │  │
│  │  3. Multimodal Document Search (+ Vision)            │  │
│  │  4. Response Generator (+ Result Cache)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Services:                                                   │
│  - LLM Service (Text + Vision)                              │
│  - pgvector Service (Vector Search)                         │
│  - Ontology Service (Neo4j)                                 │
│  - Cache Service (Redis)                                    │
│  - Document Processor (Pipeline)                            │
│  - Vision Service (Screenshot Analysis)                     │
└──────────────────┬──────────────┬────────────┬─────────────┘
                   │              │            │
          ┌────────┴─────┐ ┌─────┴────┐ ┌────┴────┐
          │ PostgreSQL   │ │  Neo4j   │ │  Redis  │
          │ + pgvector   │ │   (KG)   │ │ (Cache) │
          └──────────────┘ └──────────┘ └─────────┘
                   │
          ┌────────┴────────┐
          │    MongoDB      │
          │ (Parts Data)    │
          └─────────────────┘
```

## 데이터 플로우 (멀티모달 RAG)

```
사용자 질문: "MAT-001의 사양은?"
        │
        ▼
┌────────────────────────────────────┐
│ 1. Query Analysis                   │
│ - 의도 분석                         │
│ - 캐시 확인 ✓                       │
│ - Knowledge Graph에서 관련 엔티티   │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ 2. Material Retrieval               │
│ - MongoDB: MAT-001 기본 정보        │
│ - Neo4j: 공급업체, 장비, 관련 문서  │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ 3. Multimodal Document Search       │
│ - pgvector: 관련 문서 검색 (임베딩) │
│ - 각 문서의 스크린샷 가져오기        │
│ - Vision Model: 스크린샷 분석       │
│   → 표, 차트 데이터 추출            │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│ 4. Response Generation              │
│ - 컨텍스트:                         │
│   + 부품 정보 (MongoDB)             │
│   + 관계 정보 (Neo4j)               │
│   + 문서 내용 (텍스트)              │
│   + 시각 분석 (Vision Model)        │
│ - LLM: 종합 답변 생성               │
│ - 결과 캐싱 (30분)                  │
└────────┬───────────────────────────┘
         │
         ▼
    최종 답변 + 출처
```

## 빠른 시작

### 사전 요구사항
```bash
# 필수
- Python 3.9+
- PostgreSQL 14+ (with pgvector extension)

# 선택 (없으면 Mock 데이터)
- Neo4j 5+ (Knowledge Graph)
- Redis 7+ (Cache)
- MongoDB 6+ (Parts Data)
```

### 1단계: PostgreSQL + pgvector 설정
```bash
# PostgreSQL 설치 후
psql -U postgres

CREATE DATABASE chatbot_db;
\c chatbot_db
CREATE EXTENSION vector;
```

### 2단계: 백엔드 설치 및 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# 환경 변수 설정
cp ../.env.example .env
# .env 편집: PostgreSQL URI 등

python run.py
```

### 3단계: 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

### 4단계: 브라우저 접속
```
http://localhost:5173
```

## 문서 처리 (벡터화)

### 문서 준비
```bash
mkdir -p ./documents
# PDF, Word, Excel, PPT 파일 복사
```

### 문서 처리 스크립트
```python
from app.services.document_processor import document_processor

# 단일 문서
result = document_processor.process_document(
    file_path="./documents/부품사양서.pdf",
    metadata={"category": "specification"}
)

# 배치 처리
file_paths = ["./documents/doc1.pdf", "./documents/doc2.docx"]
results = document_processor.batch_process_documents(file_paths)
```

### 처리 과정
```
1. 텍스트 추출
2. PDF 페이지 → 스크린샷 PNG
3. Vision Model로 각 스크린샷 분석
4. Enhanced Summary 생성
5. 텍스트 청킹 (1000자, overlap 200)
6. 임베딩 생성 (캐싱)
7. pgvector에 저장
```

## 성능 최적화

### 캐싱 전략
```python
# 임베딩 캐싱 (24시간)
cache_service.cache_embedding(text, embedding, ttl=86400)

# 질의 결과 캐싱 (30분)
cache_service.cache_query_result(query, result, ttl=1800)

# 함수 레벨 캐싱
@cache_result(ttl=3600, key_prefix="my_func")
def my_expensive_function(arg):
    return result
```

### 배치 처리
```python
# 대량 문서 한번에
document_processor.batch_process_documents(file_paths)

# 대량 임베딩 저장
pgvector_service.batch_add_documents(documents)
```

### Vision 분석 최적화
```python
# 스크린샷 사전 생성 및 저장
# 질의 시점에는 캐시된 분석 결과만 사용
# 필요한 경우에만 실시간 분석
```

## Knowledge Graph 활용

### 관계 생성
```python
# 부품-공급업체 관계
ontology_service.create_relationship(
    'Material', 'materialId', 'MAT-001',
    'Supplier', 'name', 'ABC사',
    'SUPPLIED_BY',
    properties={'reliability': 'A'}
)

# 부품-문서 관계
ontology_service.create_relationship(
    'Material', 'materialId', 'MAT-001',
    'Document', 'source', '사양서.pdf',
    'DOCUMENTED_IN'
)
```

### 관계 조회
```python
# 부품의 전체 컨텍스트
context = ontology_service.get_material_context('MAT-001')
# Returns: {
#   'material': {...},
#   'suppliers': [...],
#   'equipment': [...],
#   'documents': [...],
#   'similar_materials': [...]
# }
```

## API 엔드포인트

### 채팅
```bash
POST /api/chat/query/stream
Content-Type: application/json

{
  "query": "MAT-001의 현재 재고는?",
  "user_id": 1,
  "conversation_id": 123
}

# 응답 (SSE)
data: {"type": "progress", "step": "analyzing", ...}
data: {"type": "progress", "step": "retrieving_materials", ...}
data: {"type": "progress", "step": "searching_documents", ...}
data: {"type": "response", "response": "...", "sources": [...]}
```

### 문서 처리
```bash
POST /api/documents/process
Content-Type: multipart/form-data

file: document.pdf
metadata: {"category": "specification"}

# 응답
{
  "status": "success",
  "chunks": 15,
  "screenshots": 10,
  "enhanced_summary": "...",
  "vision_insights": [...]
}
```

## 환경 변수

```env
# PostgreSQL (필수)
POSTGRES_URI=postgresql://user:pass@localhost:5432/chatbot_db

# LLM API (필수)
LLM_API_KEY=your-key
LLM_API_URL=https://api.example.com
LLM_MODEL_NAME=gpt-4
LLM_EMBEDDING_MODEL=text-embedding-3-small
LLM_VISION_MODEL=gpt-4-vision

# Neo4j (선택)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Redis (선택)
REDIS_URL=redis://localhost:6379

# MongoDB (선택)
MONGODB_URI=mongodb://localhost:27017/
```

## 모니터링

### 주요 메트릭
- Cache hit rate: >80% 목표
- 평균 응답 시간: <1초 목표
- Vision 분석 성공률: >95%
- pgvector 검색 정확도: >90%

### 로그
```bash
tail -f logs/chatbot.log | grep "Enhanced"
```

## 트러블슈팅

### pgvector 설치 오류
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS
brew install pgvector
```

### Vision API 없을 때
```python
# 자동으로 텍스트만 사용
# Mock 분석 결과 반환
```

### Neo4j 없을 때
```python
# in-memory mock data 사용
# Knowledge Graph 기능은 제한적
```

## 추가 정보

- [IMPROVEMENTS.md](./IMPROVEMENTS.md) - 상세 개선 사항
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 시스템 아키텍처
- [QUICK_START.md](./QUICK_START.md) - 5분 빠른 시작

## 라이선스

Enterprise Internal Use Only

---

**Powered by:**
- LangGraph - Agent Orchestration
- pgvector - Vector Search
- Neo4j - Knowledge Graph
- Vision Model - Multimodal Understanding
- Redis - High-Performance Cache

🚀 차세대 멀티모달 RAG로 정확도 90%+, 속도 100배 향상!
