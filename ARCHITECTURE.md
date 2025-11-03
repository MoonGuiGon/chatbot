# 시스템 아키텍처 상세 설명

## 전체 시스템 개요

이 챗봇 시스템은 **멀티 에이전트 RAG (Retrieval-Augmented Generation)** 아키텍처를 기반으로 합니다.

## 레이어 구조

### 1. 프레젠테이션 레이어 (Frontend)

**React + TypeScript + MUI**

```
User Interface
    │
    ├── ChatArea (채팅 영역)
    │   ├── MessageBubble (메시지 표시)
    │   └── ProgressIndicator (진행상황)
    │
    ├── ChatInput (입력 영역)
    │
    ├── Sidebar (대화 목록)
    │
    └── SettingsDialog (설정)
```

**상태 관리 (Zustand)**
- 대화 목록
- 현재 메시지
- 스트리밍 상태
- 사용자 설정

### 2. API 레이어 (Backend - Flask)

**REST API + SSE Streaming**

```
API Routes
    │
    ├── /api/chat/*         (채팅 엔드포인트)
    ├── /api/conversations/* (대화 관리)
    ├── /api/settings/*     (설정)
    ├── /api/feedback/*     (피드백)
    └── /api/export/*       (데이터 export)
```

### 3. 비즈니스 로직 레이어 (LangGraph Agent)

**LangGraph 멀티 노드 워크플로우**

#### 노드 1: Query Analyzer
```python
def analyze_query_node(state):
    """
    - 사용자 질문 의도 분석
    - 자재코드 추출 (정규식)
    - 필요한 데이터 소스 결정
    - LLM을 통한 의도 분류
    """
    return state
```

#### 노드 2: Material Retriever
```python
def retrieve_material_data_node(state):
    """
    - MongoDB에서 부품 정보 조회
    - 자재코드 기반 검색
    - 재고, 구매, 출고, 장착 이력 포함
    """
    return state
```

#### 노드 3: Document Searcher
```python
def search_documents_node(state):
    """
    - VectorDB에서 관련 문서 검색
    - 임베딩 유사도 기반
    - 상위 N개 문서 반환
    """
    return state
```

#### 노드 4: Response Generator
```python
def generate_response_node(state):
    """
    - 수집된 컨텍스트로 프롬프트 구성
    - LLM 호출하여 답변 생성
    - 출처 정보 포함
    - 환각 방지 지침 적용
    """
    return state
```

### 4. 데이터 레이어

#### PostgreSQL (관계형 DB)
```sql
users               -- 사용자
conversations       -- 대화
messages            -- 메시지
user_settings       -- 설정
feedbacks           -- 피드백
knowledge_entries   -- 학습 데이터
```

#### MongoDB (문서형 DB)
```javascript
{
  materialId: "MAT-001",
  name: "부품명",
  category: "카테고리",
  specifications: {...},
  inventory: {...},
  purchase_history: [...],
  usage_history: [...],
  installation_history: [...]
}
```

#### VectorDB (Chroma)
```
Document Chunks + Embeddings
├── PDF 문서
├── Word 문서
├── Excel 문서
└── PowerPoint 문서
```

## 데이터 플로우

### 일반 질의 플로우

```
1. User Input
   "MAT-001 부품의 현재 재고는?"
        │
        ▼
2. Frontend (Zustand)
   - 상태 업데이트
   - API 호출
        │
        ▼
3. Backend API
   POST /api/chat/query/stream
        │
        ▼
4. LangGraph Agent
   ┌──────────────────┐
   │ Analyze Query    │
   │ Intent: material │
   │ Material ID: 001 │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Retrieve from    │
   │ MongoDB          │
   │ → MAT-001 data   │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Search VectorDB  │
   │ (optional)       │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Generate Response│
   │ with LLM         │
   └────────┬─────────┘
            │
            ▼
5. Stream Response (SSE)
   data: {"type": "progress", "step": "analyzing", ...}
   data: {"type": "progress", "step": "retrieving_materials", ...}
   data: {"type": "response", "response": "...", ...}
        │
        ▼
6. Frontend Update
   - 진행상황 표시
   - 최종 응답 렌더링
   - 출처 표시
```

### 피드백 학습 플로우

```
1. User gives feedback
   (rating, comment)
        │
        ▼
2. Store in PostgreSQL
   feedbacks table
        │
        ▼
3. If positive (rating >= 4)
        │
        ▼
4. Create/Update knowledge_entry
   - query_pattern
   - answer
   - confidence_score++
        │
        ▼
5. Future similar queries
   → Check knowledge_entries first
   → Use learned answer if match
```

## 핵심 설계 원칙

### 1. Separation of Concerns
- **프레젠테이션**: React 컴포넌트
- **상태 관리**: Zustand
- **비즈니스 로직**: LangGraph Agents
- **데이터 접근**: Service 레이어

### 2. Scalability
- **수평 확장**: 스테이트리스 API
- **데이터베이스 샤딩**: MongoDB 파티셔닝
- **캐싱**: Redis 추가 가능

### 3. Reliability
- **Fallback 메커니즘**: DB 연결 실패 시 Mock 데이터
- **에러 핸들링**: 각 노드에서 에러 처리
- **재시도 로직**: API 호출 실패 시 재시도

### 4. Security
- **환경 변수**: 민감 정보 분리
- **입력 검증**: SQL Injection 방지
- **CORS**: 허용된 도메인만 접근
- **사내 LLM**: 데이터 외부 유출 방지

## 성능 최적화

### 1. 백엔드
- **비동기 처리**: 독립적 노드 병렬 실행 가능
- **스트리밍**: SSE로 실시간 응답
- **Connection Pooling**: DB 연결 풀

### 2. 프론트엔드
- **코드 스플리팅**: Vite 자동 처리
- **메모이제이션**: React.memo, useMemo
- **가상 스크롤**: 대화 목록 최적화

### 3. 데이터베이스
- **인덱싱**: material_id, user_id 등
- **임베딩 캐싱**: 동일 쿼리 재사용
- **배치 처리**: 대량 데이터 처리

## 확장 포인트

### 1. 새로운 데이터 소스 추가
```python
def new_data_source_node(state):
    # 새로운 데이터 소스 노드 추가
    return state

# 그래프에 노드 추가
workflow.add_node("new_source", new_data_source_node)
workflow.add_edge("analyze_query", "new_source")
```

### 2. 새로운 에이전트 추가
```python
class NewAgent:
    def __init__(self):
        self.graph = self._build_custom_graph()

    def process(self, input):
        return self.graph.invoke(input)
```

### 3. 멀티모달 지원
```python
def vision_analysis_node(state):
    """이미지 분석 노드"""
    image_data = state.get("image")
    # Vision LLM 호출
    return state
```

## 모니터링 및 로깅

### 로그 레벨
- **INFO**: 일반 작업 흐름
- **WARNING**: 비정상이지만 처리 가능한 상황
- **ERROR**: 오류 발생

### 메트릭
- API 응답 시간
- LLM 호출 횟수
- 피드백 점수 추이
- 데이터베이스 쿼리 성능

## 배포 전략

### 개발 환경
```bash
# Mock 데이터로 로컬 실행
python backend/run.py
npm run dev --prefix frontend
```

### 스테이징 환경
```bash
# 실제 DB 연결, 테스트 LLM API
docker-compose up -d
```

### 프로덕션 환경
```bash
# 실제 사내 환경
# - 사내 LLM API
# - 프로덕션 DB
# - 로드 밸런서
# - 모니터링 시스템
```

## 결론

이 아키텍처는:
- **유연성**: 새로운 노드/에이전트 쉽게 추가
- **확장성**: 수평 확장 가능
- **안정성**: Fallback 및 에러 처리
- **성능**: 스트리밍 및 비동기 처리
- **보안**: 사내 시스템 연동

을 모두 고려한 엔터프라이즈급 설계입니다.
