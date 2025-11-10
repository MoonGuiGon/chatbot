# 🤖 반도체 부품 챗봇 시스템

LangGraph 기반의 지능형 반도체 부품 관리 챗봇 시스템입니다.

## ✨ 주요 기능

- 🔍 **RAG 시스템**: MongoDB + pgvector 하이브리드 검색
- 🧠 **LangGraph**: 멀티 에이전트 워크플로우
- 💾 **메모리 시스템**: 단기/장기 기억 관리
- 📊 **데이터 시각화**: 자동 표/차트 생성 (Markdown + JSON)
- 💬 **대화 관리**: 이력 저장, 제목 자동 생성, 삭제/수정
- 📝 **피드백 수집**: 사용자 만족도 추적
- 🎨 **Modern UI**: React + MUI + Recharts

---

## 🚀 빠른 시작

### 방법 1: Mock 모드 (무료, 즉시 테스트)

```bash
# 자동 설정 및 실행
./start_test.sh
```

브라우저에서 http://localhost:3000 접속

### 방법 2: 실제 환경 (MongoDB + PostgreSQL + OpenAI API)

```bash
# 1. 자동 설정
./setup_local.sh

# 2. API Key 설정
# backend/.env 파일에서 다음 수정:
#   TEST_MODE=False
#   LLM_API_KEY=sk-your-openai-api-key

# 3. 서버 실행
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev  # 새 터미널

# 4. 브라우저 접속
# http://localhost:3000
```

**상세 가이드**: [QUICKSTART.md](QUICKSTART.md), [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)

---

## 📋 사전 요구사항

### Mock 모드 (테스트용)
- Python 3.10+
- Node.js 18+

### 실제 환경
- Docker Desktop
- Python 3.10+
- Node.js 18+
- OpenAI API Key 또는 사내 LLM API

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + MUI + Recharts + ReactMarkdown + remark-gfm       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/SSE
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (Flask)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              LangGraph Workflow                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │  Query   │→ │  Data    │→ │    Response      │  │  │
│  │  │ Analysis │  │ Retrieval│  │   Generation     │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────┐  ┌─────────────────────────────┐    │
│  │  Memory Service  │  │      LLM Service            │    │
│  │  - Short-term    │  │  - Chat (GPT-4/3.5)         │    │
│  │  - Long-term     │  │  - Embedding (ada-002)      │    │
│  └──────────────────┘  └─────────────────────────────┘    │
└────────┬────────────────────────┬───────────────────────────┘
         │                        │
    ┌────▼─────┐           ┌──────▼────────┐
    │ MongoDB  │           │  PostgreSQL   │
    │ (부품정보)│           │  + pgvector   │
    │ - 재고   │           │  (문서/매뉴얼)│
    │ - 출고   │           │  - 임베딩     │
    │ - 장착   │           │  - 검색       │
    └──────────┘           └───────────────┘
```

---

## 📊 보고서급 답변 자동 생성

### LLM이 즉시 사용 가능한 보고서 형식으로 답변

**사용자 질문**:
```
ABC-12345 부품의 최근 3개월 출고 현황을 분석해줘
```

**LLM 자동 생성 답변**:
```markdown
# 📌 부품 ABC-12345 출고 현황 분석

ABC-12345 부품의 최근 3개월 출고 데이터를 분석한 결과, **지속적인 증가 추세**를 보이고 있습니다.

## 📊 월별 출고 현황

| 월 | 출고량 | 누적 출고량 | 전월 대비 |
|----|--------|-------------|-----------|
| 1월 | 120개 | 120개 | - |
| 2월 | 150개 | 270개 | 📈 +25% |
| 3월 | 180개 | 450개 | 📈 +20% |

## 📈 출고 추이 그래프

\`\`\`json
{
  "type": "line",
  "title": "📈 월별 출고 추이 (1-3월)",
  "data": {
    "labels": ["1월", "2월", "3월"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [120, 150, 180],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)"
    }]
  }
}
\`\`\`

## 💡 주요 인사이트

### ✅ 긍정적 지표
- **평균 월 증가율**: 22.5%
- **총 출고량**: 450개 (목표 대비 112.5% 달성)

### ⚠️ 주의사항
- 4월 예상 출고: 약 216개
- 재고 준비 필요

## 📎 출처

- 부품 관리 시스템 (MongoDB)
- 출고 이력 DB (2024년 1-3월)
```

**화면 표시**:
- ✅ 📌 이모지로 섹션 구분 (가독성 ↑)
- ✅ Markdown 표 → MUI Table (깔끔한 디자인)
- ✅ JSON 차트 → Recharts (반응형 그래프)
- ✅ 계층 구조 (#, ##, ###) 유지
- ✅ 💡 인사이트 자동 생성
- ✅ 📎 출처 자동 표시

**특징**:
- 🎯 **바로 보고서로 사용 가능**: 복사-붙여넣기만으로 완성
- 📊 **전문적 구조**: 요약 → 데이터 → 인사이트 → 출처
- 🎨 **시각적 가독성**: 이모지 + 계층 구조 + 강조

**상세 가이드**: [REPORT_STYLE_GUIDE.md](REPORT_STYLE_GUIDE.md), [MARKDOWN_TABLE_AND_CHART_GUIDE.md](MARKDOWN_TABLE_AND_CHART_GUIDE.md)

---

## 🗂️ 프로젝트 구조

```
chatbot/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph 에이전트
│   │   │   ├── chatbot_agent.py
│   │   │   ├── graph_state.py
│   │   │   └── nodes.py
│   │   ├── routes/          # API 라우트
│   │   ├── services/        # 핵심 서비스
│   │   │   ├── llm_service.py
│   │   │   ├── database_service.py
│   │   │   ├── memory_service.py
│   │   │   └── document_processor.py
│   │   └── config.py
│   ├── tests/
│   │   └── mocks/           # Mock LLM/DB
│   ├── scripts/
│   │   ├── seed_mongodb.py   # 샘플 데이터 생성
│   │   └── seed_pgvector.py  # 문서 임베딩 생성
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   └── MessageBubble.jsx  # 표/차트 렌더링
│   │   │   ├── Sidebar/
│   │   │   └── Document/
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml       # MongoDB + PostgreSQL
├── init-pgvector.sql        # pgvector 초기화
├── start_test.sh           # Mock 모드 실행
├── setup_local.sh          # 실제 환경 설정
├── QUICKSTART.md           # 빠른 시작
├── LOCAL_SETUP_GUIDE.md    # 로컬 환경 설정 가이드
└── README.md               # 이 파일
```

---

## 🧪 테스트

### Mock 모드 테스트

```bash
./start_test.sh
# http://localhost:3000 접속
# 무료, 즉시 테스트 가능
```

### 실제 환경 테스트

```bash
# 1. Docker 시작
docker-compose up -d

# 2. 샘플 데이터 생성
cd backend
source venv/bin/activate
python scripts/seed_mongodb.py     # MongoDB 부품 데이터
python scripts/seed_pgvector.py    # pgvector 문서 (OpenAI API 사용)

# 3. 서버 실행
python run.py

# 4. Frontend (새 터미널)
cd frontend
npm run dev
```

**테스트 시나리오**: [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md#-step-5-실제-테스트)

---

## 🔧 환경 설정

### Backend (.env)

```bash
# 모드 선택
TEST_MODE=True          # Mock 모드 (무료)
TEST_MODE=False         # 실제 모드 (API 사용)

# Flask
FLASK_PORT=5001

# OpenAI API (실제 모드)
LLM_CHAT_URL=https://api.openai.com/v1/chat/completions
LLM_EMBEDDING_URL=https://api.openai.com/v1/embeddings
LLM_API_KEY=sk-your-api-key-here
LLM_CHAT_MODEL=gpt-4              # 또는 gpt-3.5-turbo (저렴)
LLM_EMBEDDING_MODEL=text-embedding-ada-002

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=semiconductor_chatbot

# PostgreSQL + pgvector
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=vectordb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

### Frontend (vite.config.js)

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
```

---

## 📊 비용 정보

### Mock 모드
- **비용**: 무료
- **제한**: 미리 정의된 응답만 가능

### 실제 환경 (OpenAI API)

**초기 설정**:
- MongoDB 샘플 데이터: 무료
- pgvector 문서 임베딩 (7개): **$0.01**

**사용 중** (GPT-4 기준):
- 질문 1회: $0.05 - $0.10
- 일 100회: **$5 - $10**

**비용 절감**:
```bash
# GPT-3.5 사용 (약 10배 저렴)
LLM_CHAT_MODEL=gpt-3.5-turbo
```

---

## 🎯 주요 기능 상세

### 1. RAG (Retrieval Augmented Generation)

- **하이브리드 검색**: MongoDB (구조화 데이터) + pgvector (문서)
- **임베딩**: OpenAI text-embedding-ada-002
- **유사도 검색**: Cosine similarity (pgvector)
- **컨텍스트 구성**: Top-K 문서 자동 선택

### 2. 표와 차트 자동 생성

- **Markdown 표**: `remark-gfm` → MUI Table
- **JSON 차트**: LLM 생성 → Recharts 렌더링
- **차트 타입**: Line, Bar, Pie
- **반응형**: ResponsiveContainer

**가이드**: [MARKDOWN_TABLE_AND_CHART_GUIDE.md](MARKDOWN_TABLE_AND_CHART_GUIDE.md)

### 3. 대화 관리

- **자동 저장**: 모든 대화 MongoDB 저장
- **제목 생성**: LLM이 대화 내용 기반 제목 자동 생성
- **편집/삭제**: 인라인 편집, 삭제 기능
- **이력 관리**: 사이드바에서 과거 대화 조회

### 4. 메모리 시스템

- **단기 기억**: 최근 5개 대화 턴
- **장기 기억**: 사용자 선호도, 중요 정보 추출
- **컨텍스트**: 대화 맥락 유지

### 5. 피드백 수집

- **긍정/부정**: 각 응답에 대한 피드백
- **추적**: MongoDB 저장
- **분석**: 만족도 통계 (향후 기능)

---

## 🚀 배포

### Docker Compose (전체 스택)

```bash
# 프로덕션 배포
docker-compose -f docker-compose.prod.yml up -d
```

### 개별 배포

**Backend**:
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**Frontend**:
```bash
cd frontend
npm run build
npm install -g serve
serve -s dist -p 3000
```

---

## 📚 문서

- **[QUICKSTART.md](QUICKSTART.md)**: 3분 안에 시작하기
- **[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)**: 로컬 환경 상세 가이드
- **[MARKDOWN_TABLE_AND_CHART_GUIDE.md](MARKDOWN_TABLE_AND_CHART_GUIDE.md)**: 표/차트 시각화
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: 테스트 가이드
- **[CONVERSATION_MANAGEMENT_GUIDE.md](CONVERSATION_MANAGEMENT_GUIDE.md)**: 대화 관리

---

## 🛠️ 기술 스택

### Backend
- **Framework**: Flask 3.0
- **AI**: LangChain, LangGraph, OpenAI API
- **Database**: MongoDB, PostgreSQL + pgvector
- **Language**: Python 3.10+

### Frontend
- **Framework**: React 18
- **UI**: Material-UI (MUI)
- **Charts**: Recharts
- **Markdown**: react-markdown + remark-gfm
- **Build**: Vite

### Infrastructure
- **Container**: Docker, Docker Compose
- **Database**: MongoDB 7.0, PostgreSQL + pgvector

---

## 🔍 문제 해결

### Docker 관련

```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs semiconductor_mongodb
docker logs semiconductor_postgres

# 재시작
docker-compose restart

# 완전 재시작
docker-compose down
docker-compose up -d
```

### API 오류

**OpenAI API Key 오류**:
1. `backend/.env`에서 `LLM_API_KEY` 확인
2. `sk-`로 시작하는지 확인
3. 서버 재시작

**403 오류**:
- Backend 서버가 실행 중인지 확인
- 포트 5001 확인: `lsof -i :5001`

### 표/차트 렌더링

**표가 텍스트로 표시됨**:
```bash
cd frontend
npm install remark-gfm rehype-raw
npm run dev
```

**차트가 JSON으로 표시됨**:
- 브라우저 Hard Refresh: Cmd+Shift+R
- 개발자 도구(F12) → Console에서 에러 확인

---

## 🤝 기여

이슈와 PR을 환영합니다!

---

## 📄 라이선스

MIT License

---

## 🙏 감사

- LangChain, LangGraph
- OpenAI
- MongoDB, PostgreSQL, pgvector
- React, MUI, Recharts

---

## 📞 지원

문제가 있으면 [Issues](../../issues)에 등록하거나 문서를 참조하세요.

**Happy Coding! 🎉**
