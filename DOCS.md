# 📚 반도체 부품 챗봇 시스템 - 통합 문서

> LangGraph 기반 RAG 챗봇 시스템의 모든 것

---

## 📑 목차

1. [빠른 시작](#-빠른-시작)
2. [시스템 아키텍처](#-시스템-아키텍처)
3. [주요 기능](#-주요-기능)
4. [설치 및 실행](#-설치-및-실행)
5. [스트리밍 구현](#-스트리밍-구현)
6. [보고서급 답변](#-보고서급-답변)
7. [로컬 테스트](#-로컬-테스트)
8. [문제 해결](#-문제-해결)

---

## 🚀 빠른 시작

### 30초 안에 시작하기

```bash
# Mock 모드 (무료, 즉시 테스트)
./start_test.sh

# 브라우저에서
# http://localhost:3000
```

### 실제 환경 (MongoDB + PostgreSQL + OpenAI)

```bash
# 1. 자동 설정
./setup_local.sh

# 2. API Key 입력
# backend/.env 파일:
#   TEST_MODE=False
#   LLM_API_KEY=sk-your-api-key

# 3. 서버 실행
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev  # 새 터미널
```

**자세한 내용**: [QUICKSTART.md](QUICKSTART.md), [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)

---

## 🏗️ 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────┐
│         Frontend (React + MUI)          │
│  - 보고서급 답변 렌더링                 │
│  - 실시간 스트리밍 (SSE)                │
│  - 표/차트 자동 생성                    │
└─────────────┬───────────────────────────┘
              │ HTTP/SSE
┌─────────────▼───────────────────────────┐
│         Backend (Flask)                 │
│  ┌─────────────────────────────────┐   │
│  │   LangGraph Workflow            │   │
│  │  Query → Retrieval → Response   │   │
│  └─────────────────────────────────┘   │
│  - RAG (MongoDB + pgvector)            │
│  - LLM Integration (OpenAI/사내)       │
│  - Memory System                        │
└─────────┬──────────────┬────────────────┘
          │              │
    ┌─────▼────┐   ┌─────▼────────┐
    │ MongoDB  │   │ PostgreSQL   │
    │ 부품정보 │   │ + pgvector   │
    └──────────┘   └──────────────┘
```

### 핵심 기술

| 레이어 | 기술 스택 |
|--------|-----------|
| **Frontend** | React 18, MUI, Recharts, react-markdown |
| **Backend** | Flask 3.0, LangChain, LangGraph |
| **Database** | MongoDB 7.0, PostgreSQL + pgvector |
| **AI** | OpenAI API (GPT-4, text-embedding-ada-002) |
| **Deploy** | Docker, Docker Compose |

---

## 🎯 주요 기능

### 1. 보고서급 답변 자동 생성

LLM이 **즉시 사용 가능한 보고서 형식**으로 답변을 생성합니다.

**입력**:
```
ABC-12345 부품의 최근 3개월 출고 현황을 분석해줘
```

**출력**:
```markdown
# 📌 부품 ABC-12345 출고 현황 분석

ABC-12345 부품의 최근 3개월 출고 데이터를 분석한 결과,
**지속적인 증가 추세**를 보이고 있습니다.

## 📊 월별 출고 현황

| 월 | 출고량 | 누적 | 전월 대비 |
|----|--------|------|-----------|
| 1월 | 120개 | 120개 | - |
| 2월 | 150개 | 270개 | 📈 +25% |
| 3월 | 180개 | 450개 | 📈 +20% |

[차트 JSON 블록]

## 💡 주요 인사이트

### ✅ 긍정적 지표
- 평균 월 증가율: 22.5%
- 총 출고량: 450개

### ⚠️ 주의사항
- 4월 예상 출고: 216개
- 재고 준비 필요

## 📎 출처
- 부품 관리 시스템 (MongoDB)
```

**특징**:
- ✅ 이모지로 섹션 구분 (가독성 ↑)
- ✅ 계층 구조 (#, ##, ###)
- ✅ 표와 그래프 자동 생성
- ✅ 인사이트 자동 추출
- ✅ 출처 명시
- ✅ 바로 복사-붙여넣기 가능

**자세한 내용**: [REPORT_STYLE_GUIDE.md](REPORT_STYLE_GUIDE.md)

### 2. 실시간 스트리밍 (SSE)

**기존 방식**:
```
질문 → [30초 대기] → 응답
```

**스트리밍 방식**:
```
질문 → [질문 분석 중...] → [데이터 검색 중...] → [응답 생성 중...] → 완료
       ↑ 실시간 피드백
```

**구현**:
- Backend: Flask SSE (Server-Sent Events)
- Frontend: EventSource API
- 진행 상황 실시간 표시
- 취소 가능

**자세한 내용**: [STREAMING_GUIDE.md](STREAMING_GUIDE.md)

### 3. 표와 차트 자동 생성

**Markdown 표**:
```markdown
| 부품번호 | 재고 | 상태 |
|---------|------|------|
| ABC-001 | 1500 | ✅ |
```
→ MUI Table로 자동 렌더링

**JSON 차트**:
```json
{
  "type": "line",
  "title": "월별 추이",
  "data": { ... }
}
```
→ Recharts로 자동 렌더링

**지원 차트**:
- Line Chart (추이)
- Bar Chart (비교)
- Pie Chart (비율)

**자세한 내용**: [MARKDOWN_TABLE_AND_CHART_GUIDE.md](MARKDOWN_TABLE_AND_CHART_GUIDE.md)

### 4. RAG (Retrieval Augmented Generation)

**하이브리드 검색**:
- **MongoDB**: 구조화된 부품 정보 (재고, 출고, 장착)
- **pgvector**: 문서/매뉴얼 (사양, 절차)
- **LLM**: 컨텍스트 기반 응답 생성

**특징**:
- Hallucination 최소화
- 출처 명시
- 신뢰도 점수
- Top-K 검색

### 5. 메모리 시스템

**단기 메모리**:
- 최근 5개 대화 턴
- 대화 맥락 유지

**장기 메모리**:
- 사용자 선호도
- 중요 정보 추출
- 영구 저장

**자세한 내용**: [MEMORY_GUIDE.md](MEMORY_GUIDE.md)

### 6. 대화 관리

- ✅ 자동 제목 생성 (LLM)
- ✅ 제목 수정 (인라인 편집)
- ✅ 대화 삭제
- ✅ 대화 이력 조회
- ✅ 시간순 정렬

**자세한 내용**: [CONVERSATION_MANAGEMENT_GUIDE.md](CONVERSATION_MANAGEMENT_GUIDE.md)

---

## 💻 설치 및 실행

### 요구사항

**Mock 모드**:
- Python 3.10+
- Node.js 18+

**실제 환경**:
- Docker Desktop
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 설치

#### 방법 1: 자동 설정 (추천)

```bash
./setup_local.sh
```

#### 방법 2: 수동 설정

```bash
# 1. Docker 시작
docker-compose up -d

# 2. Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env 설정
cp .env.example .env
# TEST_MODE=False
# LLM_API_KEY=sk-...

# 3. Frontend
cd ../frontend
npm install

# 4. 샘플 데이터 (선택)
cd ../backend
python scripts/seed_mongodb.py
python scripts/seed_pgvector.py
```

### 실행

```bash
# Backend (터미널 1)
cd backend
source venv/bin/activate
python run.py
# → http://localhost:5001

# Frontend (터미널 2)
cd frontend
npm run dev
# → http://localhost:3000
```

### 종료

```bash
# 서버 종료
./stop_test.sh

# Docker 종료
docker-compose down
```

---

## 🌊 스트리밍 구현

### Backend (Flask + SSE)

```python
@bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    def generate():
        agent = get_chatbot_agent()
        for event in agent.stream(query=message, ...):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(generate(), mimetype="text/event-stream")
```

### Frontend (React + EventSource)

```javascript
const eventSource = chatAPI.sendMessageStream(
  { message: "질문", user_id: "user123" },

  // 진행 상황
  (progress) => console.log('Progress:', progress),

  // 완료
  (final) => console.log('Complete:', final),

  // 에러
  (error) => console.error('Error:', error)
);

// 취소
eventSource.close();
```

### 이벤트 타입

```javascript
// 진행 상황
{
  "type": "progress",
  "data": {
    "stage": "query_analysis",
    "message": "질문 분석 중..."
  }
}

// 최종 응답
{
  "type": "final",
  "data": {
    "content": "응답 내용...",
    "sources": [...]
  }
}

// 에러
{
  "type": "error",
  "data": {
    "error": "ConnectionError",
    "message": "연결 실패"
  }
}
```

**전체 가이드**: [STREAMING_GUIDE.md](STREAMING_GUIDE.md)

---

## 📊 보고서급 답변

### 시스템 프롬프트

LLM이 다음 형식으로 자동 응답:

```markdown
# 📌 제목 (H1)

한 줄 요약

## 📊 섹션 (H2)

### 세부 항목 (H3)

| 표 | 데이터 |
|----|--------|
| 값 | 값 |

```json
{ "type": "chart", ... }
```

## 💡 인사이트

### ✅ 긍정적
- 항목

### ⚠️ 주의
- 항목

## 📎 출처
- 시스템명
```

### 이모지 가이드

| 이모지 | 용도 |
|--------|------|
| 📌 | 제목, 요약 |
| 📊 | 데이터, 통계 |
| 📈/📉 | 증가/감소 |
| 💡 | 인사이트 |
| 🔍 | 상세 분석 |
| 📎 | 출처 |
| ✅ | 정상 |
| ⚠️ | 주의 |
| ❌ | 오류 |

**전체 가이드**: [REPORT_STYLE_GUIDE.md](REPORT_STYLE_GUIDE.md)

---

## 🧪 로컬 테스트

### MongoDB + PostgreSQL + OpenAI API

**1. 자동 설정**:
```bash
./setup_local.sh
```

**2. API Key 설정**:
```bash
# backend/.env
TEST_MODE=False
LLM_API_KEY=sk-your-openai-api-key
```

**3. 서버 실행**:
```bash
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev
```

**4. 테스트**:
- http://localhost:3000 접속
- "ABC-12345 부품의 재고를 알려줘" 입력

**예상 비용**:
- 초기 설정: $0.01
- 테스트 10회: $0.50 ~ $1.00

**절감**:
```bash
# GPT-3.5 사용 (10배 저렴)
LLM_CHAT_MODEL=gpt-3.5-turbo
```

**전체 가이드**: [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)

---

## 🔧 문제 해결

### Docker 관련

```bash
# 컨테이너 확인
docker ps

# 로그 확인
docker logs semiconductor_mongodb
docker logs semiconductor_postgres

# 재시작
docker-compose restart

# 완전 재시작
docker-compose down && docker-compose up -d
```

### API 오류

**OpenAI API Key 오류**:
```
AuthenticationError: Incorrect API key
```

**해결**:
1. `backend/.env`에서 `LLM_API_KEY` 확인
2. `sk-`로 시작하는지 확인
3. 서버 재시작

**403 오류**:
```bash
# Backend 서버 확인
lsof -i :5001

# 재시작
cd backend && python run.py
```

### 표/차트 렌더링

**표가 텍스트로 표시**:
```bash
cd frontend
npm install remark-gfm rehype-raw
npm run dev
```

**차트가 JSON으로 표시**:
- Cmd+Shift+R (브라우저 Hard Refresh)
- F12 → Console에서 에러 확인

### 스트리밍 문제

**응답이 버퍼링됨**:
```nginx
# Nginx 설정
location /api/chat/stream {
    proxy_buffering off;
    proxy_cache off;
}
```

**연결이 끊김**:
```python
# Heartbeat 추가
def generate():
    for event in agent.stream(...):
        yield f"data: {json.dumps(event)}\n\n"
        yield f": heartbeat\n\n"  # 30초마다
```

**한글 깨짐**:
```python
# ensure_ascii=False
yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
```

---

## 📚 상세 문서

### 핵심 가이드

| 문서 | 내용 | 페이지 |
|------|------|--------|
| **[QUICKSTART.md](QUICKSTART.md)** | 3분 빠른 시작 | 10 |
| **[STREAMING_GUIDE.md](STREAMING_GUIDE.md)** | SSE 스트리밍 구현 | 30 |
| **[REPORT_STYLE_GUIDE.md](REPORT_STYLE_GUIDE.md)** | 보고서급 답변 | 40 |
| **[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)** | 로컬 환경 설정 | 60 |

### 기능별 가이드

| 문서 | 내용 |
|------|------|
| [MARKDOWN_TABLE_AND_CHART_GUIDE.md](MARKDOWN_TABLE_AND_CHART_GUIDE.md) | 표/차트 생성 |
| [CONVERSATION_MANAGEMENT_GUIDE.md](CONVERSATION_MANAGEMENT_GUIDE.md) | 대화 관리 |
| [MEMORY_GUIDE.md](MEMORY_GUIDE.md) | 메모리 시스템 |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | 테스트 가이드 |

### 기술 문서

| 문서 | 내용 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 아키텍처 |
| [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) | 개발 가이드 |
| [README.md](README.md) | 프로젝트 개요 |

---

## 🎯 체크리스트

### 설치 완료
- [ ] Docker Desktop 실행 중
- [ ] MongoDB 컨테이너 실행 중
- [ ] PostgreSQL 컨테이너 실행 중
- [ ] Python 가상환경 생성
- [ ] Python 패키지 설치
- [ ] npm 패키지 설치
- [ ] OpenAI API Key 설정

### 기능 확인
- [ ] 동기 API 작동
- [ ] 스트리밍 API 작동
- [ ] MongoDB 데이터 조회
- [ ] pgvector 문서 검색
- [ ] 표 렌더링 (Markdown → MUI)
- [ ] 차트 렌더링 (JSON → Recharts)
- [ ] 보고서 형식 응답
- [ ] 대화 이력 관리

### 배포 준비
- [ ] 환경 변수 분리 (.env.production)
- [ ] Docker Compose 설정
- [ ] Nginx 설정
- [ ] 모니터링 설정
- [ ] 로그 수집
- [ ] 백업 설정

---

## 🚀 배포

### Docker Compose

```bash
# 프로덕션 배포
docker-compose -f docker-compose.prod.yml up -d
```

### 환경 변수

```bash
# .env.production
TEST_MODE=False
LLM_CHAT_URL=https://company-llm.com/v1/chat
LLM_API_KEY=company-api-key

MONGODB_URI=mongodb://prod-server:27017/
POSTGRES_HOST=prod-postgres-server
```

### Nginx 설정

```nginx
server {
    listen 80;
    server_name chatbot.company.com;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:5001;
    }

    # SSE 스트리밍
    location /api/chat/stream {
        proxy_pass http://backend:5001;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
    }
}
```

---

## 💡 팁

### 개발 모드

```bash
# Mock 모드 (빠른 개발)
TEST_MODE=True
./start_test.sh
```

### 프로덕션 모드

```bash
# 실제 LLM 사용
TEST_MODE=False
LLM_API_KEY=sk-...
```

### 비용 절감

```bash
# GPT-3.5 사용
LLM_CHAT_MODEL=gpt-3.5-turbo

# 임베딩 캐싱
ENABLE_CACHE=True
```

### 성능 최적화

```bash
# 청크 크기 조절
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Top-K 조절
TOP_K_DOCUMENTS=5
```

---

## 📞 지원

문제가 있으면 [Issues](../../issues)에 등록하거나 문서를 참조하세요.

**Happy Coding! 🎉**
