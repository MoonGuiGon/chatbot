# 🚀 빠른 시작 가이드

회사 배포 전 로컬 환경에서 MongoDB, PostgreSQL, OpenAI API를 사용하여 실제 동작을 테스트하는 가장 빠른 방법입니다.

---

## ⚡️ 3분 안에 시작하기

### 사전 준비
- ✅ Docker Desktop 실행 중
- ✅ OpenAI API Key 준비 ([발급 방법](https://platform.openai.com/api-keys))

### 1단계: 자동 설정 스크립트 실행

```bash
./setup_local.sh
```

이 스크립트가 자동으로 수행하는 작업:
- Docker로 MongoDB, PostgreSQL 실행
- Python 가상환경 생성
- 의존성 설치
- (선택) 샘플 데이터 생성

### 2단계: OpenAI API Key 설정

`backend/.env` 파일을 열고 다음 두 줄만 수정:

```bash
TEST_MODE=False  # True → False로 변경

LLM_API_KEY=sk-your-actual-api-key-here  # 실제 API Key 입력
```

### 3단계: 서버 실행

**터미널 1 (Backend)**:
```bash
cd backend
source venv/bin/activate
python run.py
```

**터미널 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

### 4단계: 브라우저에서 테스트

http://localhost:3000 접속 후 질문 입력:

```
ABC-12345 부품의 재고 현황을 알려줘
```

✅ **성공!** 실제 데이터베이스와 OpenAI API를 사용한 응답이 표시됩니다.

---

## 🧪 전체 테스트 시나리오

### 테스트 1: 부품 정보 조회 (MongoDB)

**질문**:
```
ABC-12345 부품의 재고와 출고 이력을 알려줘
```

**확인 사항**:
- [ ] MongoDB에서 부품 정보 조회
- [ ] 재고 수량 표시
- [ ] 출고 이력 표로 표시
- [ ] 출처 정보 표시

### 테스트 2: 문서 검색 (pgvector)

**질문**:
```
부품 출고 절차가 어떻게 되나요?
```

**확인 사항**:
- [ ] pgvector에서 관련 문서 검색
- [ ] 유사도 기반 검색 결과
- [ ] 단계별 절차 설명
- [ ] 출처 및 유사도 점수 표시

### 테스트 3: 데이터 시각화 (LLM이 표와 차트 생성)

**질문**:
```
ABC-12345 부품의 최근 6개월 출고 추이를 표와 그래프로 보여줘
```

**확인 사항**:
- [ ] MongoDB에서 출고 이력 조회
- [ ] LLM이 Markdown 표 생성
- [ ] LLM이 JSON 차트 데이터 생성
- [ ] 프론트엔드에서 표를 MUI Table로 렌더링
- [ ] 프론트엔드에서 차트를 Recharts로 렌더링

### 테스트 4: 복합 검색

**질문**:
```
재고가 1000개 이상인 부품들을 찾아서 표로 정리해줘
```

**확인 사항**:
- [ ] MongoDB 복합 쿼리 실행
- [ ] 필터링된 결과
- [ ] 표 형식으로 정리
- [ ] 정확한 데이터

---

## 📊 비용 정보

### 예상 비용 (OpenAI API)

**초기 설정**:
- MongoDB 샘플 데이터: 무료
- pgvector 문서 임베딩 (7개): **약 $0.01**

**테스트 사용** (GPT-4 기준):
- 질문 1회: 약 $0.05 - $0.10
- 테스트 10회: **약 $0.50 - $1.00**

### 비용 절감 방법

**1. GPT-3.5 사용** (약 10배 저렴):
```bash
# backend/.env
LLM_CHAT_MODEL=gpt-3.5-turbo
```

**2. 임베딩만 먼저 테스트**:
```bash
# pgvector 문서만 생성하고 검색 테스트
python backend/scripts/seed_pgvector.py
```

**3. Mock 모드로 먼저 테스트**:
```bash
# backend/.env
TEST_MODE=True  # 무료 Mock LLM 사용
```

---

## 🔍 문제 해결

### "MongoDB 연결 실패"

```bash
# Docker 컨테이너 상태 확인
docker ps

# MongoDB 재시작
docker-compose restart mongodb

# 로그 확인
docker logs semiconductor_mongodb
```

### "PostgreSQL 연결 실패"

```bash
# 컨테이너 재시작
docker-compose restart postgres

# pgvector 확장 확인
docker exec -it semiconductor_postgres psql -U postgres -d vectordb -c "\dx"
```

### "OpenAI API Key 오류"

```
openai.error.AuthenticationError: Incorrect API key
```

**해결**:
1. API Key가 `sk-`로 시작하는지 확인
2. `backend/.env` 파일에 올바르게 입력했는지 확인
3. 서버 재시작 (Ctrl+C 후 다시 실행)
4. API Key 권한 확인: https://platform.openai.com/api-keys

### "표나 차트가 표시되지 않음"

**해결**:
1. 브라우저 Hard Refresh: Cmd+Shift+R (Mac)
2. 개발자 도구 (F12) → Console 탭에서 에러 확인
3. Frontend 서버 재시작

---

## 📁 생성된 파일 구조

```
chatbot/
├── docker-compose.yml           # Docker 설정
├── init-pgvector.sql           # PostgreSQL 초기화 스크립트
├── setup_local.sh              # 자동 설정 스크립트
├── LOCAL_SETUP_GUIDE.md        # 상세 가이드
├── QUICKSTART.md               # 이 파일
│
├── backend/
│   ├── .env                    # 환경 변수 (여기에 API Key 입력!)
│   ├── .env.example           # 환경 변수 템플릿
│   ├── scripts/
│   │   ├── seed_mongodb.py    # MongoDB 샘플 데이터 생성
│   │   └── seed_pgvector.py   # pgvector 문서 생성
│   └── ...
│
└── frontend/
    └── ...
```

---

## 🎯 체크리스트

### 설정 완료
- [ ] Docker Desktop 실행 중
- [ ] `./setup_local.sh` 실행 완료
- [ ] `backend/.env` 파일에 OpenAI API Key 입력
- [ ] `TEST_MODE=False` 설정
- [ ] MongoDB 샘플 데이터 생성 (선택)
- [ ] pgvector 문서 생성 (선택)

### 서버 실행
- [ ] Backend 서버 5001 포트에서 실행 중
- [ ] Frontend 서버 3000 포트에서 실행 중
- [ ] http://localhost:3000 접속 가능

### 기능 테스트
- [ ] MongoDB 데이터 조회 성공
- [ ] pgvector 문서 검색 성공
- [ ] LLM이 표 생성 (Markdown)
- [ ] LLM이 차트 생성 (JSON)
- [ ] 표가 MUI Table로 렌더링
- [ ] 차트가 Recharts로 렌더링

---

## 🚀 다음 단계

### 회사 환경 배포 준비

**1. 사내 LLM으로 전환**:
```bash
# backend/.env
LLM_CHAT_URL=https://your-company-llm.com/v1/chat
LLM_EMBEDDING_URL=https://your-company-llm.com/v1/embeddings
LLM_API_KEY=your-company-api-key
```

**2. 실제 데이터베이스 연결**:
```bash
# backend/.env
MONGODB_URI=mongodb://company-server:27017/
POSTGRES_HOST=company-postgres-server
```

**3. 프로덕션 배포**:
```bash
# Docker Compose로 전체 스택 배포
docker-compose -f docker-compose.prod.yml up -d
```

---

## 💡 요약

**가장 빠른 시작 방법**:

```bash
# 1. 자동 설정
./setup_local.sh

# 2. API Key 설정
# backend/.env 파일에서 LLM_API_KEY 수정

# 3. 서버 실행
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev  # 새 터미널

# 4. 테스트
# http://localhost:3000 접속
```

**비용**: 초기 테스트 약 **$1 이하**

**시간**: 설정 5분 + 테스트 5분 = **총 10분**

**결과**: 실제 데이터베이스 + OpenAI API를 사용한 완전한 동작 확인! 🎉

---

## 📚 추가 자료

- **상세 가이드**: `LOCAL_SETUP_GUIDE.md`
- **Markdown 표/차트**: `MARKDOWN_TABLE_AND_CHART_GUIDE.md`
- **테스트 가이드**: `TESTING_GUIDE.md`
- **Docker 관리**: `docker-compose.yml`

도움이 필요하면 문서를 참조하거나 이슈를 등록하세요! 🙏
