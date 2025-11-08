# 시스템 아키텍처 상세 설계

## 1. 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         사용자 (브라우저)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────▼─────────────────────────────────────┐
│                    Frontend (React + MUI)                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Chat UI      │ Document     │ Settings     │ Analytics    │ │
│  │              │ Upload UI    │ Panel        │ Dashboard    │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│                    Zustand State Management                      │
│                        API Client (Axios)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────────┐
│                      Backend (Flask)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              LangGraph Workflow Engine                    │  │
│  │  ┌────────────┬──────────────┬──────────────────────┐   │  │
│  │  │ Query      │ RAG          │ Response             │   │  │
│  │  │ Classifier │ Orchestrator │ Generator            │   │  │
│  │  └────────────┴──────────────┴──────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐ │
│  │ Document     │ LLM          │ Database     │ Feedback    │ │
│  │ Processor    │ Service      │ Service      │ Service     │ │
│  └──────────────┴──────────────┴──────────────┴─────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
         ↓                  ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   MongoDB        │  │   pgvector       │  │   사내 LLM       │
│                  │  │                  │  │                  │
│ - parts          │  │ - document_      │  │ - Chat API       │
│ - conversations  │  │   chunks         │  │ - Embedding API  │
│ - feedback       │  │ - image_         │  │ - Vision API     │
│ - doc_metadata   │  │   embeddings     │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 2. LangGraph 워크플로우 상세

### 2.1 워크플로우 흐름

```python
START
  ↓
┌──────────────────────────────────────────────────────────────┐
│ Node 1: Query Analysis & Classification                      │
│                                                               │
│ Input:  query, llm_config, custom_prompt                     │
│ Process:                                                      │
│   1. LLM을 사용하여 쿼리 분석                                 │
│   2. Intent 분류 (part_search, document_search, etc.)       │
│   3. Entity 추출 (부품번호, 부품명, 날짜, 메트릭)            │
│   4. 필요한 데이터 소스 결정                                  │
│ Output: classification                                        │
└──────────────────┬───────────────────────────────────────────┘
                   ↓
            [조건부 라우팅]
        데이터 필요? → Yes / No
                   ↓
         ┌─────────┴─────────┐
         ↓                   ↓
      [retrieve]          [direct]
         ↓                   ↓
┌──────────────────┐    [Response Generation으로]
│ Node 2: Data     │
│ Retrieval        │
│                  │
│ Process:         │
│   1. MongoDB     │
│      검색        │
│   2. pgvector    │
│      검색        │
│   3. 결과 통합   │
└────────┬─────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│ Node 3: Response Generation                                  │
│                                                               │
│ Input:  query, retrieved_documents, custom_prompt            │
│ Process:                                                      │
│   1. Context 구성 (검색 결과 → 프롬프트)                     │
│   2. Custom Prompt 적용                                      │
│   3. LLM 호출 (답변 생성)                                    │
│   4. 표/그래프 데이터 추출                                   │
│   5. 출처 정보 수집                                          │
│ Output: response (content, sources, table, chart)            │
└──────────────────┬───────────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────────────┐
│ Node 4: Quality Check & Validation                           │
│                                                               │
│ Process:                                                      │
│   1. 출처 존재 확인                                          │
│   2. 신뢰도 점수 계산                                        │
│   3. Hallucination 검증                                      │
│   4. 경고 메시지 생성                                        │
│ Output: validated response with warnings                     │
└──────────────────┬───────────────────────────────────────────┘
                   ↓
                  END
```

### 2.2 GraphState 구조

```python
GraphState = {
    # 입력
    "query": str,                    # 사용자 질문
    "user_id": Optional[str],        # 사용자 ID
    "conversation_id": Optional[str],# 대화 ID
    "custom_prompt": Optional[str],  # 커스텀 프롬프트
    "llm_config": {                  # LLM 설정
        "model": str,
        "temperature": float,
        "max_tokens": int
    },

    # 중간 상태
    "classification": {              # 쿼리 분류 결과
        "intent": str,
        "data_sources": List[str],
        "entities": Dict,
        "requires_calculation": bool,
        "response_format": str
    },
    "retrieved_documents": List[{   # 검색된 문서
        "content": str,
        "source": str,
        "metadata": Dict,
        "similarity_score": float
    }],

    # 출력
    "response": {                   # 최종 응답
        "content": str,
        "sources": List[Dict],
        "confidence_score": float,
        "table_data": Optional[List],
        "chart_data": Optional[Dict],
        "warnings": List[str]
    },

    # 진행 상황
    "progress": List[{
        "stage": str,
        "status": str,
        "message": str
    }],

    # 에러
    "error": Optional[str]
}
```

## 3. 데이터 흐름

### 3.1 채팅 메시지 처리 흐름

```
User Input
    ↓
Frontend (ChatInput)
    ↓ POST /api/chat
Backend (chat.py)
    ↓
ChatbotAgent.invoke()
    ↓
LangGraph Workflow
    ↓
    ├─→ Query Analysis (LLM)
    ├─→ Data Retrieval (MongoDB + pgvector)
    ├─→ Response Generation (LLM)
    └─→ Quality Check
    ↓
Response
    ↓
MongoDB (대화 저장)
    ↓
Frontend (MessageBubble)
    ↓
User sees response
```

### 3.2 문서 업로드 및 검수 흐름

```
User uploads file
    ↓
Frontend (DocumentUpload)
    ↓ POST /api/documents/upload
Backend (document.py)
    ↓
DocumentProcessor.process_for_review()
    ├─→ DocumentParser (파일 파싱)
    ├─→ DocumentChunker (청킹)
    └─→ Preview 데이터 생성
    ↓
Frontend (ReviewPanel)
    ↓ User reviews chunks
    ↓ POST /api/documents/{id}/approve
Backend
    ↓
DocumentProcessor.finalize_document()
    ├─→ Embedding 생성
    └─→ pgvector 저장
    ↓
MongoDB (메타데이터 저장)
    ↓
Complete
```

## 4. 데이터베이스 스키마

### 4.1 MongoDB Collections

```javascript
// parts - 부품 정보
{
  _id: ObjectId,
  part_number: "ABC-12345",
  part_name: "반도체 칩 A",
  category: "IC",
  inventory: {
    total_stock: 1000,
    available: 850,
    reserved: 150,
    last_updated: ISODate
  },
  shipment_history: [{
    date: ISODate,
    quantity: 100,
    destination: "라인 1"
  }],
  installation_records: [{
    equipment_id: "EQ-001",
    installed_date: ISODate,
    status: "active"
  }],
  inspection_data: [{
    inspection_date: ISODate,
    parameters: { voltage, current, temperature },
    result: "pass"
  }]
}

// conversations - 대화 이력
{
  _id: ObjectId,
  conversation_id: "conv_abc123",
  user_id: "user123",
  messages: [{
    role: "user|assistant",
    content: "...",
    sources: [...],
    confidence_score: 0.85,
    timestamp: ISODate
  }],
  created_at: ISODate
}

// feedback - 사용자 피드백
{
  _id: ObjectId,
  conversation_id: "conv_abc123",
  query: "...",
  response: "...",
  feedback_type: "positive|negative|neutral",
  user_comment: "...",
  user_correction: "...",
  sources_used: [...],
  created_at: ISODate
}
```

### 4.2 PostgreSQL (pgvector) Tables

```sql
-- document_chunks - 문서 청크
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    chunk_type VARCHAR(50),  -- text, table, image
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunks_embedding
ON document_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_chunks_document
ON document_chunks (document_id);

CREATE INDEX idx_chunks_metadata
ON document_chunks USING GIN (metadata);
```

## 5. API 엔드포인트

### 5.1 Chat API
```
POST   /api/chat              - 메시지 전송 (동기)
POST   /api/chat/stream       - 메시지 전송 (스트리밍)
GET    /api/conversations     - 대화 목록
GET    /api/conversations/:id - 특정 대화 조회
POST   /api/conversations     - 새 대화 생성
```

### 5.2 Document API
```
POST   /api/documents/upload          - 문서 업로드
POST   /api/documents/:id/approve     - 문서 승인
DELETE /api/documents/:id/reject      - 문서 거부
GET    /api/documents                 - 문서 목록
DELETE /api/documents/:id             - 문서 삭제
```

### 5.3 Settings API
```
GET    /api/settings                  - 설정 조회
POST   /api/settings/llm              - LLM 설정 업데이트
GET    /api/settings/models           - 사용 가능한 모델 목록
```

### 5.4 Feedback API
```
POST   /api/feedback                  - 피드백 제출
GET    /api/feedback/stats            - 피드백 통계
GET    /api/feedback/recent           - 최근 피드백
GET    /api/feedback/improvements     - 개선 제안
```

## 6. 확장성 및 최적화

### 6.1 확장 포인트
1. **LangGraph 노드 추가**
   - `backend/app/agents/nodes.py`에 새 노드 추가
   - `chatbot_agent.py`에서 워크플로우 연결

2. **새로운 데이터 소스 추가**
   - `database_service.py`에 새 서비스 추가
   - `DataRetrievalNode`에 검색 로직 추가

3. **커스텀 문서 파서**
   - `document_processor.py`의 `DocumentParser`에 새 파서 추가

### 6.2 성능 최적화 전략
1. **캐싱**
   - 자주 검색되는 쿼리 결과 캐시
   - 임베딩 캐시

2. **병렬 처리**
   - MongoDB와 pgvector 검색 병렬화
   - 다중 문서 임베딩 배치 처리

3. **인덱싱**
   - pgvector HNSW 인덱스 최적화
   - MongoDB 복합 인덱스

## 7. 보안 고려사항

1. **API 키 관리**
   - 환경 변수로 관리
   - .env 파일은 .gitignore에 추가

2. **입력 검증**
   - 파일 업로드 크기 제한
   - 파일 타입 검증

3. **출력 검증**
   - XSS 방지 (React는 자동 이스케이프)
   - SQL Injection 방지 (ORM 사용)

## 8. 모니터링 및 로깅

### 추가 개발 필요
1. **로깅**
   - 각 LangGraph 노드별 로깅
   - API 요청/응답 로깅

2. **메트릭**
   - 응답 시간
   - 신뢰도 점수 분포
   - 피드백 비율

3. **알람**
   - 에러율 임계값 초과 시
   - 응답 시간 지연 시
