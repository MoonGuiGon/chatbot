# 반도체 부품 챗봇 시스템

반도체 회사를 위한 부품 정보 질문 답변 챗봇 시스템입니다.

## 주요 기능

### 1. 스마트 RAG 시스템
- **다중 데이터 소스**: MongoDB (부품 정보) + pgvector (문서 검색)
- **쿼리 분류**: LLM이 질문을 분석하여 최적의 데이터 소스 선택
- **Hallucination 최소화**: 출처 기반 답변, 신뢰도 점수, 품질 검증

### 2. 문서 처리 파이프라인
- **다중 포맷 지원**: PDF, PPT, Excel, Word
- **멀티모달 처리**: 텍스트 + 표 + 이미지/그래프 추출
- **검수 시스템**: 사용자가 검수 후 VectorDB 저장

### 3. 사용자 경험
- **실시간 진행 상황 표시**: LLM 처리 단계별 시각화
- **표/그래프 자동 생성**: 데이터를 시각적으로 표현
- **출처 제공 및 다운로드**: 모든 답변에 출처 첨부

### 4. 피드백 및 학습
- **사용자 피드백**: 👍👎 버튼, 수정 제안
- **자동 학습**: 피드백 기반 Few-shot Learning

### 5. 메모리 시스템
- **단기 메모리**: 현재 대화 컨텍스트 유지
- **장기 메모리**: 사용자 정보 영구 저장 (선호도, 역할, 업무 등)
- **자동 학습**: 10개 메시지마다 중요 정보 자동 추출

### 6. 대화 이력 관리
- **자동 제목 생성**: LLM이 대화 내용 분석하여 제목 자동 생성
- **제목 수정**: 인라인 편집으로 간편한 제목 변경
- **대화 삭제**: 불필요한 대화 관리
- **시간순 정렬**: 최신 대화가 위로

### 7. 커스터마이징
- **LLM 설정**: Model, Temperature 선택
- **Custom Prompt**: 시스템 프롬프트 커스터마이징

## 기술 스택

### Backend
- **Framework**: Flask
- **LLM 워크플로우**: LangGraph
- **LLM**: 사내 LLM (OpenAI 호환)
- **Database**: MongoDB (부품 정보), PostgreSQL + pgvector (문서)
- **문서 처리**: PyPDF, python-pptx, openpyxl, python-docx

### Frontend
- **Framework**: React (JavaScript + JSX)
- **상태 관리**: Zustand
- **UI**: Material-UI (MUI)
- **차트**: Recharts

## 프로젝트 구조

```
chatbot/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph 워크플로우
│   │   │   ├── graph_state.py
│   │   │   ├── nodes.py
│   │   │   └── chatbot_agent.py
│   │   ├── services/        # 핵심 서비스
│   │   │   ├── llm_service.py
│   │   │   ├── database_service.py
│   │   │   └── document_processor.py
│   │   ├── routes/          # API 엔드포인트
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   ├── settings.py
│   │   │   └── feedback.py
│   │   └── config.py
│   ├── tests/               # 테스트용 Mock (쉽게 제거 가능)
│   │   └── mocks/
│   │       ├── mock_llm.py
│   │       └── mock_db.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat/
│   │   │       ├── MessageBubble.jsx
│   │   │       ├── ChatInput.jsx
│   │   │       ├── ChatArea.jsx
│   │   │       └── ProgressIndicator.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── store/
│   │   │   └── chatStore.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── start_test.sh            # 테스트 모드 시작
├── stop_test.sh             # 서버 종료
└── README.md
```

## 빠른 시작 (테스트 모드)

### 1. 테스트 모드로 실행
DB와 LLM 없이 Mock 데이터로 테스트할 수 있습니다.

```bash
# 실행 권한 부여
chmod +x start_test.sh stop_test.sh

# 서버 시작
./start_test.sh
```

자동으로 다음이 실행됩니다:
- Backend 서버: http://localhost:5000
- Frontend 서버: http://localhost:3000

### 2. 브라우저에서 접속
```
http://localhost:3000
```

### 3. 테스트 질문 예시
```
- 부품 ABC-12345의 재고는?
- 반도체 칩 A의 최근 출고 이력을 알려줘
- 부품 검사 절차가 뭐야?
```

### 4. 서버 종료
```bash
./stop_test.sh
```

## 실제 환경 설정

### 1. Backend 설정

#### 환경 변수 설정 (.env)
```bash
# 테스트 모드 비활성화
TEST_MODE=False

# 사내 LLM 설정
LLM_API_KEY=your-real-api-key
LLM_CHAT_URL=https://common.llm.com/v1/chat/completions
LLM_EMBEDDING_URL=https://embedding.llm.com/v1/embeddings
LLM_VISION_URL=https://vision.llm.com/v1/chat/completions

# MongoDB
MONGODB_URI=mongodb://your-server:27017/
MONGODB_DATABASE=semiconductor_chatbot

# PostgreSQL
POSTGRES_HOST=your-postgres-server
POSTGRES_PORT=5432
POSTGRES_DATABASE=vectordb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

#### Backend 실행
```bash
cd backend

# 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python run.py
```

### 2. Frontend 실행
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
```

## API 문서

### Chat API

#### POST /api/chat
메시지 전송 (동기)

**Request:**
```json
{
  "message": "부품 ABC-12345의 재고는?",
  "user_id": "user123",
  "conversation_id": "conv-xyz",
  "custom_prompt": "당신은 친절한 챗봇입니다",
  "llm_config": {
    "model": "gpt-4",
    "temperature": 0.1
  }
}
```

**Response:**
```json
{
  "success": true,
  "content": "부품 ABC-12345의 현재 재고는...",
  "sources": [...],
  "confidence_score": 0.85,
  "table_data": [...],
  "chart_data": {...},
  "warnings": []
}
```

### Document API

#### POST /api/documents/upload
문서 업로드

**Request:**
```
multipart/form-data
file: [File]
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc_abc123",
  "review_data": {
    "chunks": [...]
  }
}
```

#### POST /api/documents/{document_id}/approve
문서 승인 및 VectorDB 저장

**Request:**
```json
{
  "chunks": [
    {
      "chunk_index": 0,
      "content": "...",
      "approved": true,
      "metadata": {...}
    }
  ]
}
```

## Mock 시스템 제거 방법

테스트가 완료되면 Mock 시스템을 제거할 수 있습니다:

```bash
# Mock 폴더 삭제
rm -rf backend/tests/

# Mock import 제거
# backend/app/services/llm_service.py 의 if config.test_mode: 부분 삭제
# backend/app/services/database_service.py 의 if config.test_mode: 부분 삭제
```

## LangGraph 워크플로우

```
User Query
    ↓
┌─────────────────────┐
│ Query Analysis      │ ← LLM이 질문 분석
│ - Intent 분류       │
│ - Entity 추출       │
│ - 데이터 소스 결정  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Data Retrieval      │
│ - MongoDB 검색      │ ← 부품 정보
│ - pgvector 검색     │ ← 문서 검색
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Response Generation │
│ - Context 구성      │
│ - LLM 답변 생성     │
│ - 표/그래프 추출    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Quality Check       │
│ - Hallucination 검증│
│ - 신뢰도 계산       │
│ - 경고 생성         │
└──────────┬──────────┘
           ↓
      Final Output
```

## 개발 로드맵

### Phase 1: 기반 구조 ✅
- [x] 프로젝트 구조 생성
- [x] Mock 시스템 구현
- [x] LangGraph 워크플로우
- [x] 기본 UI

### Phase 2: 문서 처리 (다음 단계)
- [ ] Vision API 통합 (표/그래프 추출)
- [ ] Semantic Chunking 개선
- [ ] 문서 검수 UI 완성

### Phase 3: 고급 기능
- [ ] 스트리밍 응답
- [ ] Few-shot Learning 자동화
- [ ] 캐시 시스템
- [ ] Analytics 대시보드

### Phase 4: 최적화
- [ ] 응답 속도 개선
- [ ] Re-ranking 알고리즘
- [ ] Hybrid Search 최적화

## 문제 해결

### Backend 서버가 시작되지 않음
```bash
# 포트 충돌 확인
lsof -i :5000

# 프로세스 종료
kill -9 <PID>
```

### Frontend 빌드 오류
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### Mock LLM 응답 커스터마이징
`backend/tests/mocks/mock_llm.py`의 응답 로직 수정

## 라이선스

MIT License

## 개발자

PM: Claude Code Assistant

## 기여

Issue 및 PR 환영합니다!
