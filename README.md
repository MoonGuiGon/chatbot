# Enterprise Chatbot - 반도체 부품 관리 AI 시스템

LangGraph 기반 멀티 에이전트 RAG 시스템으로 구축된 엔터프라이즈급 챗봇입니다.

## 주요 기능

### 핵심 기능
- **멀티 소스 RAG**: MongoDB(부품 정보) + VectorDB(문서) 통합 검색
- **LangGraph 에이전트 시스템**: 질문 분석 → 데이터 검색 → 답변 생성의 체계적 워크플로우
- **실시간 스트리밍**: SSE 기반 실시간 응답 및 진행상황 시각화
- **피드백 학습**: 사용자 피드백을 통한 지속적 개선
- **개인화**: 맞춤 프롬프트 설정 및 대화 기록 관리

### 데이터 소스
- **MongoDB**: 부품 정보, 재고, 구매/출고/장착 이력
- **VectorDB (Chroma)**: 문서(PDF, Word, Excel, PPT) 임베딩
- **PostgreSQL**: 대화 기록, 사용자 설정, 피드백, 학습 데이터

### 진행상황 시각화
챗봇이 답변을 생성하는 과정을 단계별로 시각화:
1. 질문 분석 중...
2. MongoDB에서 부품 정보 조회 중...
3. VectorDB에서 관련 문서 검색 중...
4. 답변 생성 중...

## 프로젝트 구조

```
chatbot/
├── backend/                 # Flask 백엔드
│   ├── app/
│   │   ├── agents/         # LangGraph 에이전트
│   │   │   ├── graph_state.py      # 상태 정의
│   │   │   ├── nodes.py             # 노드 함수들
│   │   │   └── chatbot_agent.py    # 메인 에이전트
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── routes/         # API 엔드포인트
│   │   ├── services/       # 서비스 레이어
│   │   └── config.py       # 설정
│   ├── requirements.txt
│   └── run.py
│
└── frontend/               # React 프론트엔드
    ├── src/
    │   ├── components/     # UI 컴포넌트
    │   │   ├── Chat/       # 채팅 관련
    │   │   └── Settings/   # 설정 관련
    │   ├── store/          # Zustand 상태 관리
    │   ├── services/       # API 서비스
    │   ├── types/          # TypeScript 타입
    │   └── App.tsx
    └── package.json
```

## 시작하기

### 사전 요구사항
- Python 3.9+
- Node.js 18+
- PostgreSQL (선택사항, SQLite로 대체 가능)
- MongoDB (선택사항, Mock 데이터 사용 가능)

### 백엔드 설정

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp ../.env.example .env
# .env 파일을 열어 필요한 값 입력

# 서버 실행
python run.py
```

### 프론트엔드 설정

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env

# 개발 서버 실행
npm run dev
```

## 환경 변수 설정

### 백엔드 (.env)

```env
# Database
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=chatbot_db
POSTGRES_URI=postgresql://user:password@localhost:5432/chatbot_db

# LLM (사내 LLM API)
LLM_API_KEY=your-api-key
LLM_API_URL=https://your-internal-llm-api.com
LLM_MODEL_NAME=your-model-name
LLM_EMBEDDING_MODEL=your-embedding-model
LLM_VISION_MODEL=your-vision-model

# VectorDB
VECTORDB_TYPE=chroma
VECTORDB_PATH=./vectordb_data

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
PORT=5000
```

### 프론트엔드 (.env)

```env
VITE_API_URL=http://localhost:5000
```

## Mock 데이터로 테스트하기

데이터베이스나 LLM API 설정 없이도 테스트 가능합니다:

1. **자동 Fallback**: 연결 실패 시 자동으로 Mock 데이터 사용
2. **In-Memory DB**: SQLite in-memory 데이터베이스 자동 생성
3. **Mock LLM**: 사전 정의된 응답 반환

```bash
# 환경 변수 없이 바로 실행
cd backend
python run.py

# 다른 터미널에서
cd frontend
npm run dev
```

브라우저에서 http://localhost:5173 접속

## 주요 API 엔드포인트

### 채팅
- `POST /api/chat/query` - 일반 질의
- `POST /api/chat/query/stream` - 스트리밍 질의

### 대화 관리
- `GET /api/conversations/` - 대화 목록
- `GET /api/conversations/{id}` - 특정 대화 조회
- `POST /api/conversations/` - 새 대화 생성
- `DELETE /api/conversations/{id}` - 대화 삭제

### 설정
- `GET /api/settings/{user_id}` - 사용자 설정 조회
- `PUT /api/settings/{user_id}` - 설정 업데이트
- `POST /api/settings/{user_id}/prompts` - 맞춤 프롬프트 추가

### 피드백
- `POST /api/feedback/` - 피드백 제출
- `GET /api/feedback/stats` - 피드백 통계
- `GET /api/feedback/knowledge` - 학습된 지식 조회

### Export
- `POST /api/export/material` - 부품 데이터 Excel 다운로드
- `GET /api/export/conversation/{id}` - 대화 내용 텍스트 다운로드

## 아키텍처

### LangGraph 에이전트 워크플로우

```
┌─────────────────┐
│  Query Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Analyze Query Node     │  ← 질문 의도 분석
│  - 부품 정보 필요?      │
│  - 문서 검색 필요?      │
│  - 자재코드 추출        │
└────────┬────────────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌──────────────────┐   ┌────────────────────┐
│ Retrieve         │   │ Search Documents   │
│ Material Data    │   │ from VectorDB      │
│ from MongoDB     │   │                    │
└────────┬─────────┘   └──────┬─────────────┘
         │                    │
         └──────────┬─────────┘
                    │
                    ▼
         ┌────────────────────────┐
         │ Generate Response Node │
         │ - LLM을 통한 답변 생성 │
         │ - 출처 정보 포함        │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Final Response │
         └────────────────┘
```

### 핵심 기술 스택

**백엔드:**
- Flask - 웹 프레임워크
- LangGraph - 에이전트 오케스트레이션
- LangChain - LLM 인터페이스
- SQLAlchemy - ORM
- ChromaDB - 벡터 데이터베이스
- Pandas - 데이터 처리 및 Excel export

**프론트엔드:**
- React 18 + TypeScript
- Vite - 빌드 도구
- MUI (Material-UI) - UI 컴포넌트
- Zustand - 상태 관리
- Axios - HTTP 클라이언트
- React Markdown - 마크다운 렌더링

## 환각(Hallucination) 방지 전략

1. **컨텍스트 기반 응답**: 제공된 데이터만 사용
2. **출처 명시**: 모든 정보의 출처 표시
3. **확실성 검증**: 불확실한 경우 명시적 표현
4. **사용자 피드백**: 부정확한 응답 개선

## 성능 최적화

- **스트리밍 응답**: SSE를 통한 실시간 응답
- **진행상황 표시**: 사용자 대기 시간 체감 감소
- **캐싱**: VectorDB 검색 결과 캐싱
- **비동기 처리**: 독립적 작업 병렬 처리

## 보안 고려사항

- **환경 변수**: 민감 정보 분리
- **CORS**: Frontend 도메인만 허용
- **입력 검증**: SQL Injection, XSS 방지
- **사내 LLM**: 데이터 외부 유출 방지

## 향후 개선 사항

- [ ] 멀티모달 지원 (이미지, 차트 분석)
- [ ] 실시간 협업 기능
- [ ] 고급 분석 대시보드
- [ ] A/B 테스트 프레임워크
- [ ] 음성 인터페이스
- [ ] 모바일 앱

## 라이선스

Enterprise Internal Use Only

## 문의

기술 지원 및 문의사항은 내부 Slack 채널 #chatbot-support로 연락주세요.
