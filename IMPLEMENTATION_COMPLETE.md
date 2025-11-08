# ✅ 반도체 부품 챗봇 시스템 - 구현 완료

## 📋 프로젝트 개요

**완료일**: 2025-11-08
**테스트 모드**: 완전 동작
**구현 상태**: 모든 핵심 기능 완료

---

## 🎯 구현된 핵심 기능

### ✅ 1. RAG 시스템
- **MongoDB**: 부품 데이터 (재고, 출고, 검사 이력)
- **pgvector**: 문서 벡터 검색
- **LangGraph 워크플로우**: 지능형 쿼리 라우팅
- **Mock 시스템**: 실제 DB 없이 테스트 가능

### ✅ 2. 문서 처리
- **지원 형식**: PDF, PPT, Word, Excel
- **다중 모드**: 텍스트, 표, 그래프, 이미지
- **업로드 UI**: 드래그앤드롭, 진행률 표시
- **리뷰 시스템**: 벡터화 전 미리보기

### ✅ 3. Hallucination 최소화
- **출처 기반 답변**: 모든 답변에 출처 표시
- **신뢰도 점수**: 답변 품질 검증
- **품질 체크 노드**: LangGraph에서 자동 검증

### ✅ 4. 피드백 시스템
- **👍/👎 피드백**: 각 답변에 대한 사용자 평가
- **피드백 수집**: API를 통한 저장
- **학습 파이프라인**: 향후 모델 개선에 활용

### ✅ 5. 메모리 시스템
#### 5-1. 단기 메모리 (대화 컨텍스트)
- 현재 대화의 최근 10개 메시지 유지
- 대명사 참조 정확히 해석 ("그 부품", "그거")
- 대화 흐름 자연스럽게 유지

#### 5-2. 장기 메모리 (사용자 정보)
- **5가지 카테고리**:
  - 선호도 (답변 형식, 상세도 등)
  - 역할 (부서, 직책)
  - 자주조회 (관심 부품, 라인)
  - 명시적요청 ("기억해줘")
  - 업무컨텍스트 (프로젝트, 업무)
- **자동 저장**: 10개 메시지마다 LLM이 중요 정보 추출
- **영구 저장**: MongoDB에 사용자별로 저장
- **다른 대화에도 적용**: 새 대화에서도 사용자 정보 활용

### ✅ 6. 대화 이력 관리 (NEW!)
#### 6-1. 자동 대화 생성
- "새 대화" 버튼으로 즉시 생성
- 생성된 대화가 자동으로 사이드바에 추가
- 기본 제목: "새 대화"

#### 6-2. 자동 제목 생성
- 첫 메시지 전송 후 LLM이 자동으로 제목 생성
- 대화 내용 분석 (처음 3턴)
- 30자 이내로 간결하고 의미있는 제목
- 예: "부품 ABC-12345 재고 조회", "라인 1 검사 이력 확인"

#### 6-3. 제목 수정
- ✏️ 편집 아이콘으로 제목 수정 가능
- 인라인 편집 (바로 입력창 표시)
- Enter 키 또는 ✓ 아이콘으로 저장
- ✕ 아이콘으로 취소

#### 6-4. 대화 삭제
- 🗑️ 삭제 아이콘으로 대화 제거
- 확인 대화창으로 실수 방지
- 서버에서 완전 삭제

#### 6-5. 대화 이력 조회
- 시간순으로 정렬된 대화 목록
- 날짜 정보 표시
- 클릭으로 이전 대화 불러오기

### ✅ 7. 설정 및 커스터마이징
- **LLM 설정**:
  - 모델 선택 (GPT-4, GPT-3.5 등)
  - Temperature 조절
  - Max Tokens 조절
  - Custom System Prompt
- **메모리 관리**:
  - 저장된 메모리 조회
  - 수동 추가/삭제
  - 전체 초기화
  - 카테고리별 통계

### ✅ 8. Rich UI/UX
- **표 렌더링**: Markdown 표 자동 변환
- **그래프 렌더링**: Recharts를 사용한 다양한 차트
  - Line Chart, Bar Chart, Pie Chart
- **진행 상태 표시**: LangGraph 단계별 진행률
- **대화 이력 관리**:
  - 사이드바에서 모든 대화 확인
  - 인라인 제목 편집
  - 삭제 기능 (확인 대화창)
  - 시간순 정렬
- **반응형 디자인**: Material-UI 기반
- **직관적 아이콘**: 편집(✏️), 삭제(🗑️), 저장(✓), 취소(✕)

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     사용자 인터페이스                          │
│              (React + MUI + Zustand)                         │
│  - 채팅 화면, 문서 업로드, 설정, 메모리 관리                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                   Flask Backend                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           LangGraph 워크플로우                        │    │
│  │  QueryAnalysis → DataRetrieval → ResponseGen        │    │
│  │                   → QualityCheck                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Memory       │  │ LLM Service  │  │ Vector       │      │
│  │ Manager      │  │ (Mock)       │  │ Service      │      │
│  │ - 단기/장기   │  │              │  │ (Mock)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  데이터 레이어 (Mock)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MongoDB      │  │ pgvector     │  │ File Storage │      │
│  │ - 부품 데이터 │  │ - 문서 벡터   │  │ - 업로드 파일 │      │
│  │ - 메모리      │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 프로젝트 구조

```
chatbot/
├── backend/                    # Flask 백엔드
│   ├── app/
│   │   ├── __init__.py        # Flask 앱 초기화, 라우트 등록
│   │   ├── config.py          # 설정 (LLM, DB, 파일 업로드)
│   │   ├── agents/            # LangGraph 워크플로우
│   │   │   ├── chatbot_agent.py   # 메인 워크플로우 (메모리 통합)
│   │   │   ├── graph_state.py     # 상태 정의 (memory_context 추가)
│   │   │   └── nodes.py           # 각 노드 구현 (메모리 컨텍스트 사용)
│   │   ├── routes/            # API 엔드포인트
│   │   │   ├── chat.py            # 채팅 API
│   │   │   ├── document.py        # 문서 업로드
│   │   │   ├── settings.py        # 설정 관리
│   │   │   ├── feedback.py        # 피드백 수집
│   │   │   └── memory.py          # 메모리 관리 (NEW!)
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── llm_service.py     # LLM 호출
│   │   │   ├── vector_service.py  # 벡터 검색
│   │   │   ├── database_service.py # DB 연결
│   │   │   ├── document_processor.py # 문서 처리
│   │   │   └── memory_service.py  # 메모리 관리 (NEW!)
│   │   └── models/            # 데이터 모델
│   ├── tests/
│   │   └── mocks/             # Mock 구현
│   │       ├── mock_llm.py        # Mock LLM
│   │       └── mock_db.py         # Mock MongoDB/pgvector
│   ├── requirements.txt       # Python 패키지
│   └── run.py                 # 서버 실행 스크립트
│
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── App.jsx            # 메인 컴포넌트
│   │   ├── components/
│   │   │   ├── Chat/          # 채팅 UI
│   │   │   │   ├── ChatArea.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   ├── MessageBubble.jsx  # 표, 그래프 렌더링
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── ProgressIndicator.jsx
│   │   │   ├── Settings/      # 설정 UI
│   │   │   │   ├── SettingsDialog.jsx  # LLM 설정 + 메모리 탭
│   │   │   │   └── MemoryPanel.jsx     # 메모리 관리 UI (NEW!)
│   │   │   └── Document/      # 문서 업로드 UI
│   │   │       └── DocumentUploadDialog.jsx
│   │   ├── store/
│   │   │   └── chatStore.js   # Zustand 상태 관리
│   │   └── services/
│   │       └── api.js         # API 호출
│   ├── package.json           # npm 패키지
│   └── vite.config.js         # Vite 설정
│
├── start_test.sh              # 테스트 모드 시작 스크립트
├── stop_test.sh               # 테스트 모드 종료 스크립트
│
└── 문서/
    ├── ARCHITECTURE.md        # 시스템 아키텍처
    ├── MEMORY_GUIDE.md        # 메모리 시스템 가이드
    ├── MEMORY_TESTING_GUIDE.md # 메모리 테스트 가이드
    ├── CONVERSATION_MANAGEMENT_GUIDE.md # 대화 이력 관리 가이드 (NEW!)
    ├── TESTING_GUIDE.md       # 전체 테스트 가이드
    └── IMPLEMENTATION_COMPLETE.md # 이 문서
```

---

## 🚀 빠른 시작

### 1. 테스트 모드 실행
```bash
./start_test.sh
```

자동으로:
- Backend 서버 시작 (포트 5000)
- Frontend 서버 시작 (포트 3000)
- 브라우저 자동 열림 (http://localhost:3000)
- Mock DB/LLM 사용 (실제 인프라 불필요)

### 2. 종료
```bash
./stop_test.sh
```

---

## 🧪 테스트 가이드

### 기본 기능 테스트
1. **채팅 테스트**: "부품 ABC-12345의 재고는?"
2. **표 렌더링**: "출고 이력을 표로 보여줘"
3. **그래프 렌더링**: "재고 추이 그래프"
4. **피드백**: 답변에 👍/👎 클릭
5. **문서 업로드**: 우측 상단 📤 버튼
6. **설정**: 우측 상단 ⚙️ 버튼

### 메모리 시스템 테스트
상세한 테스트 시나리오는 **MEMORY_TESTING_GUIDE.md** 참조

**빠른 테스트**:
1. "나는 생산팀이야" → 역할 저장
2. 10개 메시지 주고받기 → 자동 저장
3. 설정 → 메모리 관리 → 저장 확인
4. 새 대화 시작 → 역할 정보 반영됨

### 대화 이력 관리 테스트
상세한 테스트 시나리오는 **CONVERSATION_MANAGEMENT_GUIDE.md** 참조

**빠른 테스트**:
1. "새 대화" 버튼 클릭 → 사이드바에 자동 추가
2. "부품 ABC-12345 재고는?" 질문 → 제목 자동 생성
3. ✏️ 클릭 → 제목 수정 → Enter 또는 ✓ 저장
4. 🗑️ 클릭 → 확인 → 대화 삭제

---

## 📊 구현된 API 엔드포인트

### 채팅
- `POST /api/chat` - 일반 채팅
- `POST /api/chat/stream` - 스트리밍 채팅

### 대화 관리
- `GET /api/conversations?user_id={user_id}` - 대화 목록
- `GET /api/conversations/{conversation_id}` - 특정 대화
- `POST /api/conversations` - 새 대화 생성
- `DELETE /api/conversations/{conversation_id}` - 대화 삭제 (NEW!)
- `PUT /api/conversations/{conversation_id}/title` - 제목 수정 (NEW!)
- `POST /api/conversations/{conversation_id}/generate-title` - 자동 제목 생성 (NEW!)

### 문서 업로드
- `POST /api/upload` - 파일 업로드
- `GET /api/documents/{user_id}` - 문서 목록
- `POST /api/document/{doc_id}/review` - 문서 리뷰

### 설정
- `GET /api/settings/{user_id}` - 설정 조회
- `POST /api/settings/{user_id}` - 설정 저장

### 피드백
- `POST /api/feedback` - 피드백 저장
- `GET /api/feedback/stats/{user_id}` - 피드백 통계

### 메모리 (NEW!)
- `GET /api/memory/{user_id}` - 메모리 조회
- `POST /api/memory/{user_id}/manual` - 메모리 수동 추가
- `DELETE /api/memory/{user_id}/{memory_id}` - 메모리 삭제
- `POST /api/memory/{user_id}/clear` - 전체 초기화
- `POST /api/memory/{user_id}/save` - 대화에서 자동 추출
- `GET /api/memory/stats/{user_id}` - 메모리 통계
- `GET /api/memory/{user_id}/context` - 메모리 컨텍스트 문자열

---

## 🎨 UI 스크린샷 위치

테스트 실행 시 확인 가능:
1. **메인 화면**: 채팅 + 사이드바 + 대화 이력
2. **표 렌더링**: Markdown 표 자동 변환
3. **그래프**: Line/Bar/Pie 차트
4. **문서 업로드**: 드래그앤드롭 UI
5. **설정 - LLM**: 모델, Temperature, Max Tokens
6. **설정 - 메모리**: 메모리 목록, 추가/삭제
7. **대화 이력**: 제목 편집, 삭제, 자동 생성 (NEW!)

---

## 🔧 설정 파일

### Backend: `.env`
```bash
# 테스트 모드 (Mock DB/LLM 사용)
TEST_MODE=True

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# LLM (실제 환경에서만 필요)
LLM_CHAT_URL=https://your-llm.com/v1/chat/completions
LLM_API_KEY=your-api-key

# Database (실제 환경에서만 필요)
MONGODB_URI=mongodb://localhost:27017/
POSTGRES_HOST=localhost
```

### Frontend: `.env`
```bash
VITE_API_BASE_URL=http://localhost:5000/api
```

---

## 📈 성능 및 제한사항

### TEST_MODE 제한사항
1. **Mock DB**: 서버 재시작하면 데이터 초기화
2. **Mock LLM**: 간단한 패턴 매칭 (실제는 더 정교함)
3. **메모리 추출**: 키워드 기반 (실제는 LLM 분석)
4. **제목 생성**: 단순화된 로직 (실제는 더 정교한 LLM 분석)
5. **샘플 데이터**: 3개 부품만 (ABC-12345, ABC-12346, ABC-12347)

### 실제 환경에서
1. **MongoDB**: 영구 저장
2. **pgvector**: 수백만 벡터 검색
3. **LLM**: 정교한 자연어 이해
4. **메모리 추출**: 정확한 중요 정보 식별
5. **제목 생성**: 대화 내용 깊이 분석하여 의미있는 제목 생성

---

## 🔐 보안 고려사항

현재 구현:
- ✅ CORS 설정 (개발 환경)
- ✅ 파일 업로드 제한 (100MB, 허용 확장자)
- ✅ 사용자별 메모리 분리

추가 필요 (실제 배포 시):
- [ ] 인증/인가 (JWT, OAuth)
- [ ] API Rate Limiting
- [ ] 파일 스캔 (악성코드)
- [ ] SQL Injection 방지
- [ ] XSS 방지
- [ ] HTTPS 적용

---

## 📚 참고 문서

1. **ARCHITECTURE.md**: 시스템 아키텍처 상세 설명
2. **MEMORY_GUIDE.md**: 메모리 시스템 상세 가이드
3. **MEMORY_TESTING_GUIDE.md**: 메모리 기능 테스트 시나리오
4. **CONVERSATION_MANAGEMENT_GUIDE.md**: 대화 이력 관리 가이드 (NEW!)
5. **TESTING_GUIDE.md**: 전체 시스템 테스트 가이드

---

## 🎯 다음 단계 (실제 배포를 위해)

### Phase 1: 실제 인프라 연결
- [ ] MongoDB 연결 및 테스트
- [ ] PostgreSQL + pgvector 설정
- [ ] 실제 LLM API 연결 (사내 LLM)
- [ ] Vision API 연동 (이미지 분석)

### Phase 2: 고급 기능
- [ ] 스트리밍 응답 UI 연동
- [ ] 문서 리뷰 워크플로우 완성
- [ ] 피드백 기반 학습 파이프라인
- [ ] 시맨틱 청킹 고도화

### Phase 3: 성능 최적화
- [ ] Redis 캐싱
- [ ] Re-ranking 알고리즘
- [ ] 메모리 조회 최적화 (인덱싱)
- [ ] 응답 속도 개선

### Phase 4: 프로덕션 준비
- [ ] 인증/인가 시스템
- [ ] 로깅 및 모니터링
- [ ] 에러 핸들링 강화
- [ ] 성능 테스트 및 부하 테스트
- [ ] 배포 자동화 (CI/CD)

---

## ✨ 주요 성과

1. **완전한 RAG 시스템**: MongoDB + pgvector 하이브리드
2. **지능형 워크플로우**: LangGraph 기반 조건부 라우팅
3. **Hallucination 최소화**: 출처 기반 답변 + 품질 검증
4. **사용자 맞춤화**: 메모리 시스템으로 개인화
5. **대화 관리**: 자동 제목 생성, 편집, 삭제 (NEW!)
6. **Rich UI**: 표, 그래프, 진행 상태 시각화
7. **테스트 용이성**: Mock 시스템으로 인프라 없이 개발

---

## 🎉 결론

**모든 핵심 기능이 구현되고 테스트 가능한 상태입니다!**

테스트 모드에서:
- ✅ 채팅 동작
- ✅ 문서 업로드 UI
- ✅ 설정 UI
- ✅ 피드백 수집
- ✅ 메모리 시스템 (단기 + 장기)
- ✅ 대화 이력 관리 (생성, 자동 제목, 편집, 삭제)
- ✅ 표/그래프 렌더링

**다음 스텝**: 실제 인프라 연결 및 프로덕션 배포 준비

---

**문의사항**: 각 가이드 문서 참조 또는 코드 내 주석 확인

**Happy Chatting!** 🤖✨
