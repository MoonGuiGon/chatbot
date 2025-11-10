# 📋 로컬 환경 테스트 설정 완료 요약

회사 배포 전 MongoDB, PostgreSQL, OpenAI API를 사용한 실제 테스트 환경이 준비되었습니다!

---

## ✅ 생성된 파일

### 1. Docker 설정
- **`docker-compose.yml`**: MongoDB + PostgreSQL (pgvector) 자동 실행
- **`init-pgvector.sql`**: pgvector 확장 및 테이블 자동 생성

### 2. 데이터 생성 스크립트
- **`backend/scripts/seed_mongodb.py`**: MongoDB 샘플 부품 데이터 20개 생성
- **`backend/scripts/seed_pgvector.py`**: pgvector 문서 7개 임베딩 생성

### 3. 자동 설정 스크립트
- **`setup_local.sh`**: 전체 환경 자동 설정 (Docker, Python, npm)

### 4. 문서
- **`QUICKSTART.md`**: 3분 빠른 시작 가이드
- **`LOCAL_SETUP_GUIDE.md`**: 상세 설정 및 테스트 가이드 (60페이지)
- **`README.md`**: 업데이트됨 (실제 환경 가이드 포함)

---

## 🚀 바로 시작하기

### 방법 1: 자동 설정 스크립트 (추천!)

```bash
./setup_local.sh
```

이 스크립트가 자동으로:
1. ✅ Docker로 MongoDB, PostgreSQL 실행
2. ✅ Python 가상환경 생성 및 패키지 설치
3. ✅ Frontend npm 패키지 설치
4. ✅ (선택) 샘플 데이터 생성

### 방법 2: 수동 설정

```bash
# 1. Docker 시작
docker-compose up -d

# 2. Backend 설정
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. .env 파일 수정
cp .env.example .env
# TEST_MODE=False
# LLM_API_KEY=sk-your-openai-api-key

# 4. 샘플 데이터 생성 (선택)
python scripts/seed_mongodb.py
python scripts/seed_pgvector.py

# 5. Frontend 설정
cd ../frontend
npm install

# 6. 서버 실행
cd ../backend && python run.py  # 터미널 1
cd frontend && npm run dev       # 터미널 2
```

---

## 🔑 중요: OpenAI API Key 설정

**`backend/.env` 파일에서 다음 두 줄만 수정**:

```bash
TEST_MODE=False  # True → False로 변경

LLM_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx  # 실제 API Key 입력
```

**API Key 발급**: https://platform.openai.com/api-keys

---

## 🧪 테스트 방법

### 1. 서버 실행

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

### 2. 브라우저 접속

http://localhost:3000

### 3. 테스트 질문

#### 테스트 1: MongoDB 데이터 조회
```
ABC-12345 부품의 재고 현황을 알려줘
```

**확인사항**:
- ✅ MongoDB에서 부품 정보 조회
- ✅ 재고 수량 표시
- ✅ 실제 데이터 표시

#### 테스트 2: pgvector 문서 검색
```
부품 출고 절차가 어떻게 되나요?
```

**확인사항**:
- ✅ pgvector 유사도 검색
- ✅ 관련 문서 반환
- ✅ 유사도 점수 표시

#### 테스트 3: 표와 차트 생성
```
ABC-12345 부품의 최근 6개월 출고 추이를 표와 그래프로 보여줘
```

**확인사항**:
- ✅ 실제 LLM이 Markdown 표 생성
- ✅ 실제 LLM이 JSON 차트 생성
- ✅ 표가 MUI Table로 렌더링
- ✅ 차트가 Recharts로 렌더링

---

## 📊 예상 비용

### 초기 설정
- MongoDB 샘플 데이터: **무료**
- pgvector 문서 임베딩 (7개): **약 $0.01**

### 테스트 사용 (GPT-4)
- 질문 1회: $0.05 - $0.10
- 테스트 10회: **약 $0.50 - $1.00**

### 비용 절감 방법

**GPT-3.5 사용** (10배 저렴):
```bash
# backend/.env
LLM_CHAT_MODEL=gpt-3.5-turbo
```

---

## 📁 생성된 데이터

### MongoDB (부품 데이터)
- **컬렉션**: `parts`
- **문서 수**: 20개
- **데이터 종류**:
  - 부품 번호, 이름, 카테고리
  - 재고 정보 (총량, 가용, 예약, 위치)
  - 출고 이력 (12개월)
  - 장착 이력
  - 품질 정보 (검사 합격률, 불량 유형)
  - 가격 정보

**확인 방법**:
```bash
docker exec -it semiconductor_mongodb mongosh
> use semiconductor_chatbot
> db.parts.find().pretty()
```

### PostgreSQL (문서 데이터)
- **테이블**: `documents`
- **문서 수**: 7개
- **데이터 종류**:
  - 부품 사양 (ABC-12345)
  - 출고 절차
  - 품질 검사 기준
  - 보관 조건
  - 불량 처리 프로세스
  - 장착 절차
  - 재고 관리 정책

**확인 방법**:
```bash
docker exec -it semiconductor_postgres psql -U postgres -d vectordb
> SELECT id, LEFT(content, 50), metadata FROM documents;
```

---

## 🔍 작동 확인

### 1. Docker 컨테이너

```bash
docker ps
```

**예상 출력**:
```
CONTAINER ID   IMAGE                    STATUS
abc123...      mongo:7.0                Up 2 minutes
def456...      ankane/pgvector:latest   Up 2 minutes
```

### 2. 데이터베이스 연결

```bash
cd backend
source venv/bin/activate

python -c "
from app.services.database_service import get_mongodb, get_pgvector
print('MongoDB:', get_mongodb())
print('PostgreSQL:', get_pgvector())
print('✓ 모두 연결 성공!')
"
```

### 3. 서버 상태

```bash
lsof -i :5001 -i :3000
```

**예상 출력**:
```
python3   12345   user   6u  IPv4  ... TCP *:5001 (LISTEN)
node      12346   user  32u  IPv6  ... TCP *:3000 (LISTEN)
```

---

## 🚨 문제 해결

### "Docker 연결 실패"

```bash
# Docker Desktop이 실행 중인지 확인
docker info

# Docker 재시작
docker-compose down
docker-compose up -d

# 로그 확인
docker logs semiconductor_mongodb
docker logs semiconductor_postgres
```

### "OpenAI API Key 오류"

```
AuthenticationError: Incorrect API key
```

**해결**:
1. API Key가 `sk-`로 시작하는지 확인
2. `backend/.env` 파일 저장 확인
3. Backend 서버 재시작 (Ctrl+C 후 다시 실행)

### "표나 차트가 표시되지 않음"

**해결**:
1. 브라우저 Hard Refresh: **Cmd+Shift+R** (Mac)
2. 개발자 도구(F12) → Console 탭에서 에러 확인
3. Frontend 재시작

---

## 📚 주요 문서

| 문서 | 내용 | 페이지 |
|------|------|--------|
| **QUICKSTART.md** | 3분 빠른 시작 | 간결 |
| **LOCAL_SETUP_GUIDE.md** | 상세 설정 가이드 | 60+ |
| **MARKDOWN_TABLE_AND_CHART_GUIDE.md** | 표/차트 생성 가이드 | 40+ |
| **README.md** | 프로젝트 개요 | 30+ |
| **TESTING_GUIDE.md** | 테스트 가이드 | 20+ |

---

## ✅ 체크리스트

### 설정 완료
- [ ] Docker Desktop 실행 중
- [ ] `docker-compose up -d` 실행
- [ ] MongoDB 컨테이너 실행 중
- [ ] PostgreSQL 컨테이너 실행 중
- [ ] `backend/.env` 파일에 API Key 입력
- [ ] `TEST_MODE=False` 설정
- [ ] Python 가상환경 생성
- [ ] Python 패키지 설치
- [ ] npm 패키지 설치

### 데이터 생성 (선택)
- [ ] MongoDB 샘플 데이터 20개 생성
- [ ] pgvector 문서 7개 생성
- [ ] 임베딩 정상 생성 (1536 차원)

### 서버 실행
- [ ] Backend 서버 5001 포트 실행 중
- [ ] Frontend 서버 3000 포트 실행 중
- [ ] http://localhost:3000 접속 가능

### 기능 테스트
- [ ] MongoDB 데이터 조회 성공
- [ ] pgvector 문서 검색 성공
- [ ] 유사도 점수 표시
- [ ] 실제 LLM이 표 생성
- [ ] 실제 LLM이 차트 생성
- [ ] 표가 MUI Table로 렌더링
- [ ] 차트가 Recharts로 렌더링

---

## 🎯 다음 단계

### 회사 환경 배포 준비

**1. 사내 LLM으로 전환**:
```bash
# backend/.env
LLM_CHAT_URL=https://company-llm.example.com/v1/chat
LLM_EMBEDDING_URL=https://company-llm.example.com/v1/embeddings
LLM_API_KEY=company-api-key-here
```

**2. 실제 데이터베이스 연결**:
```bash
# backend/.env
MONGODB_URI=mongodb://company-server:27017/
POSTGRES_HOST=company-postgres-server
POSTGRES_PORT=5432
```

**3. 프로덕션 배포**:
```bash
# Docker Compose로 전체 스택 배포
docker-compose -f docker-compose.prod.yml up -d
```

---

## 💡 핵심 요약

### 준비된 것
1. ✅ **Docker 설정**: MongoDB + PostgreSQL (pgvector)
2. ✅ **자동 스크립트**: `setup_local.sh`
3. ✅ **샘플 데이터**: 부품 20개 + 문서 7개
4. ✅ **상세 문서**: 150+ 페이지 가이드

### 필요한 것
1. 🔑 **OpenAI API Key** (https://platform.openai.com/api-keys)
2. 💻 **Docker Desktop** (https://www.docker.com/products/docker-desktop)

### 시작 방법
```bash
# 1. 자동 설정
./setup_local.sh

# 2. API Key 입력
# backend/.env → LLM_API_KEY=sk-xxxxx

# 3. 서버 실행
cd backend && source venv/bin/activate && python run.py
cd frontend && npm run dev  # 새 터미널
```

### 예상 비용
- 초기 테스트: **$1 이하**
- 지속적 개발: GPT-3.5 사용 시 **$0.1/일**

---

## 🎉 완료!

모든 준비가 완료되었습니다!

**다음 단계**:
1. `./setup_local.sh` 실행
2. `backend/.env`에 API Key 입력
3. 서버 실행
4. http://localhost:3000 접속
5. 테스트!

**도움말**: 문제가 있으면 `LOCAL_SETUP_GUIDE.md`의 문제 해결 섹션을 참조하세요.

**Happy Testing! 🚀**
