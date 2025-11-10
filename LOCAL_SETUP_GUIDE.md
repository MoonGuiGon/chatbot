# 🚀 로컬 환경 실제 테스트 가이드

회사에 배포하기 전에 MongoDB, PostgreSQL, OpenAI API를 사용하여 실제로 동작하는지 테스트하는 방법입니다.

---

## 📋 사전 준비물

### 1. 필수 소프트웨어
- ✅ Python 3.10 이상
- ✅ Node.js 18 이상
- ✅ Docker Desktop (MongoDB, PostgreSQL 실행용)
- ✅ OpenAI API Key

### 2. OpenAI API Key 발급
1. https://platform.openai.com/ 접속
2. 로그인 후 "API Keys" 메뉴 선택
3. "Create new secret key" 클릭
4. API Key 복사 (sk-...로 시작)

---

## 🐳 Step 1: Docker로 MongoDB와 PostgreSQL 실행

### 1-1. Docker Compose 파일 생성

프로젝트 루트에 `docker-compose.yml` 파일이 있는지 확인하세요:

```yaml
version: '3.8'

services:
  # MongoDB
  mongodb:
    image: mongo:7.0
    container_name: semiconductor_mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: semiconductor_chatbot
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  # PostgreSQL with pgvector
  postgres:
    image: ankane/pgvector:latest
    container_name: semiconductor_postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: vectordb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-pgvector.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  mongodb_data:
  postgres_data:
```

### 1-2. pgvector 초기화 스크립트 생성

`init-pgvector.sql` 파일 생성:

```sql
-- pgvector 확장 설치
CREATE EXTENSION IF NOT EXISTS vector;

-- 문서 테이블 생성
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 벡터 유사도 검색을 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 메타데이터 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS documents_metadata_idx
ON documents USING gin (metadata);
```

### 1-3. Docker 컨테이너 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 실행 확인
docker ps

# 로그 확인
docker-compose logs -f
```

**예상 출력**:
```
CONTAINER ID   IMAGE                    STATUS          PORTS
abc123...      mongo:7.0                Up 10 seconds   0.0.0.0:27017->27017/tcp
def456...      ankane/pgvector:latest   Up 10 seconds   0.0.0.0:5432->5432/tcp
```

### 1-4. 데이터베이스 연결 확인

**MongoDB 확인**:
```bash
# MongoDB에 접속
docker exec -it semiconductor_mongodb mongosh

# 데이터베이스 확인
show dbs
use semiconductor_chatbot
show collections

# 종료: exit
```

**PostgreSQL 확인**:
```bash
# PostgreSQL에 접속
docker exec -it semiconductor_postgres psql -U postgres -d vectordb

# pgvector 확장 확인
\dx

# 테이블 확인
\dt

# 종료: \q
```

---

## ⚙️ Step 2: Backend 환경 설정

### 2-1. .env 파일 생성

```bash
cd backend
cp .env.example .env
```

### 2-2. .env 파일 수정

`.env` 파일을 열고 다음과 같이 수정:

```bash
# 실제 모드로 변경!
TEST_MODE=False

# Flask 설정
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5001

# OpenAI API 설정 (실제 OpenAI 사용)
LLM_CHAT_URL=https://api.openai.com/v1/chat/completions
LLM_EMBEDDING_URL=https://api.openai.com/v1/embeddings
LLM_VISION_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-your-actual-openai-api-key-here  # 👈 여기에 실제 API Key 입력!
LLM_CHAT_MODEL=gpt-4
LLM_EMBEDDING_MODEL=text-embedding-ada-002
LLM_VISION_MODEL=gpt-4-vision-preview
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000

# MongoDB 설정
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=semiconductor_chatbot

# PostgreSQL (pgvector) 설정
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=vectordb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# 파일 업로드 설정
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=100

# RAG 설정
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_DOCUMENTS=5
CONFIDENCE_THRESHOLD=0.7

# 캐시 설정
ENABLE_CACHE=True
CACHE_TTL=3600
```

**중요**: `LLM_API_KEY`를 실제 OpenAI API Key로 교체하세요!

### 2-3. Python 가상환경 설정 및 의존성 설치

```bash
# 가상환경 생성 (아직 없다면)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2-4. 데이터베이스 연결 테스트

간단한 테스트 스크립트를 실행하여 연결을 확인:

```bash
python -c "
from app.services.database_service import get_mongodb, get_pgvector

# MongoDB 테스트
print('MongoDB 연결 테스트...')
mongodb = get_mongodb()
print('✓ MongoDB 연결 성공!')

# PostgreSQL 테스트
print('PostgreSQL 연결 테스트...')
pgvector = get_pgvector()
print('✓ PostgreSQL 연결 성공!')

print('\n모든 데이터베이스 연결 성공! 🎉')
"
```

**예상 출력**:
```
MongoDB 연결 테스트...
✓ MongoDB 연결 성공!
PostgreSQL 연결 테스트...
✓ PostgreSQL 연결 성공!

모든 데이터베이스 연결 성공! 🎉
```

---

## 📊 Step 3: 테스트 데이터 입력

### 3-1. MongoDB 샘플 데이터 생성

`backend/scripts/seed_mongodb.py` 파일 생성:

```python
"""
MongoDB 샘플 데이터 생성 스크립트
"""
from datetime import datetime, timedelta
import random
from app.services.database_service import get_mongodb
from app.config import config

def seed_parts_data():
    """부품 데이터 생성"""
    mongodb = get_mongodb()

    # 기존 데이터 삭제
    mongodb.delete_many("parts", {})

    parts = []
    part_prefixes = ["ABC", "DEF", "XYZ", "QWE", "RTY"]

    for i in range(20):
        prefix = random.choice(part_prefixes)
        part_number = f"{prefix}-{12345 + i}"

        # 출고 이력 생성
        shipment_history = []
        base_date = datetime.now() - timedelta(days=365)

        for month in range(12):
            shipment_date = base_date + timedelta(days=30 * month)
            shipment_history.append({
                "date": shipment_date.strftime("%Y-%m-%d"),
                "quantity": random.randint(50, 200),
                "destination": f"라인 {random.randint(1, 3)}",
                "status": "completed"
            })

        part = {
            "part_number": part_number,
            "part_name": f"반도체 부품 {prefix} 시리즈",
            "category": random.choice(["메모리", "프로세서", "센서", "기타"]),
            "inventory": {
                "total_stock": random.randint(500, 2000),
                "available": random.randint(300, 1500),
                "reserved": random.randint(0, 300),
                "location": f"창고 {random.choice(['A', 'B', 'C'])}"
            },
            "shipment_history": shipment_history,
            "quality_info": {
                "inspection_pass_rate": round(random.uniform(0.95, 0.99), 3),
                "defect_types": random.sample(["스크래치", "접착불량", "오염", "치수불량"], k=2)
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        parts.append(part)

    # 데이터 삽입
    result = mongodb.insert_many("parts", parts)
    print(f"✓ {len(result)} 개의 부품 데이터 생성 완료!")

    # 샘플 데이터 출력
    sample = mongodb.find_one("parts", {"part_number": parts[0]["part_number"]})
    print(f"\n샘플 데이터:")
    print(f"  부품번호: {sample['part_number']}")
    print(f"  부품명: {sample['part_name']}")
    print(f"  총 재고: {sample['inventory']['total_stock']}개")
    print(f"  출고 이력: {len(sample['shipment_history'])}건")

if __name__ == "__main__":
    print("MongoDB 샘플 데이터 생성 시작...\n")
    seed_parts_data()
    print("\n완료! 🎉")
```

**실행**:
```bash
cd backend
python scripts/seed_mongodb.py
```

### 3-2. PostgreSQL 샘플 문서 생성

`backend/scripts/seed_pgvector.py` 파일 생성:

```python
"""
pgvector 샘플 문서 생성 스크립트
"""
from app.services.database_service import get_pgvector
from app.services.llm_service import get_embedding_llm
from app.config import config

def seed_documents():
    """샘플 문서 생성 및 임베딩"""
    pgvector = get_pgvector()
    embedding_llm = get_embedding_llm()

    # 샘플 문서
    documents = [
        {
            "content": "ABC-12345 부품은 메모리 모듈로 DDR4 규격을 따릅니다. 동작 전압은 1.2V이며, 속도는 3200MHz입니다.",
            "metadata": {"part_number": "ABC-12345", "type": "specification", "category": "메모리"}
        },
        {
            "content": "부품 출고 절차: 1) 출고 요청서 작성 2) 재고 확인 3) 품질 검사 4) 포장 5) 출하",
            "metadata": {"type": "procedure", "category": "출고"}
        },
        {
            "content": "검사 기준: 스크래치 0.5mm 이하, 접착 강도 10N 이상, 오염도 육안 검사 통과",
            "metadata": {"type": "quality_standard", "category": "검사"}
        },
        {
            "content": "DEF-12346 부품의 보관 조건: 온도 15-25°C, 습도 40-60%, 정전기 방지 포장 필수",
            "metadata": {"part_number": "DEF-12346", "type": "storage", "category": "보관"}
        },
        {
            "content": "불량 처리 프로세스: 불량 발견 → 불량 분류 → 원인 분석 → 재작업/폐기 결정 → 이력 기록",
            "metadata": {"type": "procedure", "category": "품질관리"}
        },
    ]

    print("문서 임베딩 생성 중...\n")

    for i, doc in enumerate(documents, 1):
        # 임베딩 생성 (OpenAI API 호출)
        print(f"[{i}/{len(documents)}] 임베딩 생성 중: {doc['content'][:50]}...")
        embedding = embedding_llm.embed_query(doc["content"])

        # pgvector에 저장
        pgvector.insert(
            content=doc["content"],
            embedding=embedding,
            metadata=doc["metadata"]
        )
        print(f"  ✓ 저장 완료 (임베딩 차원: {len(embedding)})")

    print(f"\n✓ {len(documents)}개 문서 저장 완료!")

    # 테스트 검색
    print("\n=== 검색 테스트 ===")
    query = "부품 출고는 어떻게 하나요?"
    print(f"질문: {query}")

    query_embedding = embedding_llm.embed_query(query)
    results = pgvector.similarity_search(query_embedding, k=3)

    print(f"\n검색 결과 ({len(results)}건):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 유사도: {result.get('similarity_score', 0):.3f}")
        print(f"   내용: {result['content'][:80]}...")
        print(f"   메타데이터: {result['metadata']}")

if __name__ == "__main__":
    print("pgvector 샘플 문서 생성 시작...\n")
    print("⚠️  OpenAI API를 사용하므로 비용이 발생할 수 있습니다.")
    input("계속하려면 Enter를 누르세요...")

    seed_documents()
    print("\n완료! 🎉")
```

**실행**:
```bash
cd backend
python scripts/seed_pgvector.py
```

**예상 비용**: 약 $0.01 미만 (5개 문서 임베딩)

---

## 🚀 Step 4: 서버 실행

### 4-1. Backend 서버 실행

```bash
# backend 디렉토리에서
cd backend
source venv/bin/activate
python run.py
```

**예상 출력**:
```
========================================
반도체 부품 챗봇 서버 시작
========================================
모드: 운영 모드
포트: 5001
========================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5001
```

### 4-2. Frontend 서버 실행

새 터미널에서:

```bash
# frontend 디렉토리에서
cd frontend
npm run dev
```

**예상 출력**:
```
VITE v5.4.21  ready in 182 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

---

## 🧪 Step 5: 실제 테스트

### 5-1. 브라우저에서 테스트

**URL**: http://localhost:3000

### 5-2. 테스트 시나리오

#### 테스트 1: 부품 정보 조회
**질문**:
```
ABC-12345 부품의 재고 현황을 알려줘
```

**예상 응답**:
- MongoDB에서 부품 정보 조회
- 재고 수량, 위치 정보 표시
- 출처 표시

#### 테스트 2: 문서 검색
**질문**:
```
부품 출고 절차가 어떻게 되나요?
```

**예상 응답**:
- pgvector에서 관련 문서 검색
- 출고 절차 단계별 설명
- 출처 표시 (유사도 점수 포함)

#### 테스트 3: 데이터 시각화
**질문**:
```
ABC-12345 부품의 최근 6개월 출고 추이를 표와 그래프로 보여줘
```

**예상 응답**:
- MongoDB에서 출고 이력 조회
- Markdown 표로 월별 데이터 표시
- Line Chart로 추이 시각화
- 실제 LLM이 JSON 차트 데이터 생성

#### 테스트 4: 복합 질문
**질문**:
```
재고가 1000개 이상인 부품들의 목록과 각 부품의 검사 합격률을 표로 보여줘
```

**예상 응답**:
- MongoDB 복합 쿼리 실행
- 필터링된 결과를 표로 정리
- 검사 합격률 데이터 포함

### 5-3. OpenAI API 사용 확인

**브라우저 개발자 도구 (F12) → Network 탭**:
- `/api/chat` 요청 확인
- 응답 시간 확인 (실제 API 호출이므로 Mock보다 느림)

**Backend 로그 확인**:
```bash
# backend 터미널에서
# OpenAI API 호출 로그가 표시됨
```

---

## 📊 Step 6: 비용 모니터링

### 6-1. OpenAI 사용량 확인

1. https://platform.openai.com/usage 접속
2. 오늘 날짜의 사용량 확인
3. 예상 비용:
   - Chat (GPT-4): $0.03/1K tokens (입력), $0.06/1K tokens (출력)
   - Embedding (ada-002): $0.0001/1K tokens
   - 테스트 10회 정도: **약 $0.5 ~ $1.0**

### 6-2. 비용 절감 팁

**개발 중에는 GPT-3.5 사용**:
```bash
# .env 파일에서
LLM_CHAT_MODEL=gpt-3.5-turbo  # GPT-4 → GPT-3.5 (약 10배 저렴)
```

**Rate Limit 설정**:
```python
# backend/app/config.py
max_requests_per_minute = 10  # 분당 최대 요청 수 제한
```

---

## 🔍 Step 7: 문제 해결

### 문제 1: MongoDB 연결 실패
```
pymongo.errors.ServerSelectionTimeoutError
```

**해결**:
```bash
# Docker 컨테이너 상태 확인
docker ps

# MongoDB 재시작
docker-compose restart mongodb

# 로그 확인
docker logs semiconductor_mongodb
```

### 문제 2: PostgreSQL 연결 실패
```
psycopg2.OperationalError: could not connect to server
```

**해결**:
```bash
# PostgreSQL 재시작
docker-compose restart postgres

# 비밀번호 확인
docker exec -it semiconductor_postgres psql -U postgres -d vectordb
```

### 문제 3: OpenAI API 오류
```
openai.error.AuthenticationError: Incorrect API key
```

**해결**:
1. API Key가 올바른지 확인 (sk-...로 시작)
2. .env 파일 저장 후 서버 재시작
3. API Key 권한 확인 (https://platform.openai.com/api-keys)

### 문제 4: 임베딩 생성 실패
```
openai.error.RateLimitError: Rate limit exceeded
```

**해결**:
```python
# seed_pgvector.py에서 지연 추가
import time

for doc in documents:
    embedding = embedding_llm.embed_query(doc["content"])
    time.sleep(1)  # 1초 대기 추가
```

---

## 📝 Step 8: 테스트 체크리스트

### 데이터베이스 연결
- [ ] MongoDB 연결 성공
- [ ] PostgreSQL 연결 성공
- [ ] pgvector 확장 설치 확인

### 데이터 생성
- [ ] MongoDB 샘플 데이터 20개 생성
- [ ] PostgreSQL 문서 5개 생성
- [ ] 임베딩 정상 생성 (1536 차원)

### 서버 실행
- [ ] Backend 서버 5001 포트 실행
- [ ] Frontend 서버 3000 포트 실행
- [ ] 프록시 연결 정상

### 기능 테스트
- [ ] 부품 정보 조회 (MongoDB)
- [ ] 문서 검색 (pgvector)
- [ ] 유사도 검색 동작
- [ ] 표 생성 (Markdown → MUI Table)
- [ ] 차트 생성 (JSON → Recharts)
- [ ] 실제 LLM 응답 확인

### 성능 확인
- [ ] 응답 시간 3초 이내
- [ ] 메모리 사용량 정상
- [ ] OpenAI API 호출 성공

---

## 🎉 성공 확인

모든 테스트가 완료되면:

1. **콘솔 출력**:
```
✓ MongoDB 연결 성공
✓ PostgreSQL 연결 성공
✓ 부품 데이터 20개 생성
✓ 문서 5개 임베딩 완료
✓ 검색 테스트 성공
✓ 실제 LLM 응답 생성
```

2. **브라우저 화면**:
   - 깔끔한 MUI 표 렌더링
   - 반응형 차트 표시
   - 출처 정보 표시
   - 신뢰도 점수 표시

3. **OpenAI 사용량**:
   - 약 $0.5 ~ $1.0 비용 발생
   - 정상 동작 확인

---

## 🚀 다음 단계

### 회사 환경 배포 준비

1. **환경 변수 분리**:
```bash
# .env.development (개발)
# .env.production (운영)
```

2. **사내 LLM으로 전환**:
```bash
LLM_CHAT_URL=https://company-llm.com/v1/chat
LLM_API_KEY=company-api-key
```

3. **Docker Compose 배포**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **모니터링 설정**:
   - Prometheus + Grafana
   - 로그 수집 (ELK Stack)
   - 알림 설정 (Slack, Email)

---

## 📚 추가 자료

- **MongoDB 쿼리 가이드**: https://www.mongodb.com/docs/manual/tutorial/query-documents/
- **pgvector 문서**: https://github.com/pgvector/pgvector
- **OpenAI API 문서**: https://platform.openai.com/docs/api-reference
- **LangChain 문서**: https://python.langchain.com/docs/get_started/introduction

---

## 💡 요약

**준비 단계**:
1. Docker로 MongoDB, PostgreSQL 실행
2. .env 파일에 OpenAI API Key 설정
3. 샘플 데이터 생성 (MongoDB + pgvector)

**테스트 단계**:
1. Backend/Frontend 서버 실행
2. 브라우저에서 질문 테스트
3. 표와 차트 생성 확인
4. OpenAI API 호출 확인

**비용**:
- 초기 테스트: 약 $0.5 ~ $1.0
- 지속적 개발: GPT-3.5 사용 권장

**다음 단계**:
- 회사 환경 배포
- 사내 LLM 전환
- 모니터링 설정

모든 준비 완료! 🎉
