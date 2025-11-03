# 빠른 시작 가이드

## 5분 안에 시작하기

이 가이드는 DB나 LLM API 설정 없이 Mock 데이터로 챗봇을 바로 테스트할 수 있도록 합니다.

### 1단계: 저장소 클론 (이미 완료)

```bash
cd chatbot
```

### 2단계: 백엔드 실행

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (Mock 데이터 자동 사용)
python run.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 3단계: 프론트엔드 실행

**새 터미널을 열고:**

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 4단계: 브라우저에서 접속

브라우저에서 http://localhost:5173 를 엽니다.

### 5단계: 챗봇 테스트

다음과 같은 질문을 시도해보세요:

1. **부품 정보 조회**
   ```
   MAT-001 부품의 현재 재고는 얼마인가요?
   ```

2. **문서 검색**
   ```
   부품 보관 방법에 대해 알려주세요
   ```

3. **복합 질의**
   ```
   MAT-001 부품의 사양과 관련 지침을 알려주세요
   ```

## Mock 데이터 설명

### 자동으로 제공되는 Mock 데이터:

1. **MongoDB (부품 정보)**
   - MAT-001, MAT-002, MAT-003 샘플 부품
   - 재고, 구매이력, 사용이력, 장착이력 포함

2. **VectorDB (문서)**
   - 부품관리지침.pdf
   - 부품사양서_MAT001.docx
   - 2024Q1_구매현황.pptx
   - 장착이력_2024_03.xlsx
   - 품질관리기준.pdf

3. **LLM 응답**
   - 사전 정의된 응답 패턴
   - 스트리밍 효과 시뮬레이션

## 주요 기능 테스트

### 1. 대화 생성 및 관리
- 좌측 사이드바에서 "새 대화" 클릭
- 여러 대화를 만들어 전환 테스트
- 대화 삭제 테스트

### 2. 진행상황 시각화
- 질문 입력 후 단계별 진행상황 확인:
  - ✓ 질문 분석
  - ✓ MongoDB 조회
  - ✓ VectorDB 검색
  - ✓ 답변 생성

### 3. 출처 표시
- 답변 하단의 "출처 (N)" 클릭
- MongoDB 데이터와 문서 출처 확인

### 4. 부품 데이터 테이블
- 부품 정보가 포함된 답변에서 표 확인
- "Excel 다운로드" 버튼으로 export 테스트

### 5. 피드백
- 답변에 👍 또는 👎 클릭
- 상세 피드백 제공

### 6. 맞춤 프롬프트
- 좌측 상단 "설정" 클릭
- 맞춤 프롬프트 추가
  - 예: "답변은 항상 3줄 이내로 요약해주세요"
- 새 질문에 자동 적용 확인

## 실제 환경 연결하기

Mock 데이터로 테스트 후, 실제 환경에 연결하려면:

### 1. 환경 변수 설정

```bash
# 백엔드 디렉토리에서
cp ../.env.example .env

# .env 파일 편집
# - MongoDB URI
# - PostgreSQL URI
# - LLM API 정보
```

### 2. 데이터베이스 준비

**PostgreSQL:**
```sql
CREATE DATABASE chatbot_db;
```

**MongoDB:**
```javascript
// 데이터베이스와 컬렉션 자동 생성됨
```

### 3. VectorDB 데이터 추가

```python
# 문서 임베딩 스크립트 (별도 제공)
python scripts/embed_documents.py --input ./documents
```

### 4. 서버 재시작

```bash
# 백엔드
python run.py

# 프론트엔드
npm run dev
```

## 문제 해결

### 포트가 이미 사용 중인 경우

**백엔드 (5000):**
```bash
# .env 파일에서
PORT=5001
```

**프론트엔드 (5173):**
```bash
# vite.config.ts에서 포트 변경
```

### 의존성 설치 오류

**Python:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

**Node:**
```bash
npm cache clean --force
npm install
```

### 브라우저 연결 오류

1. CORS 확인: `.env`에서 `FRONTEND_URL` 확인
2. 백엔드 서버 실행 확인: http://localhost:5000/health
3. 브라우저 콘솔에서 에러 메시지 확인

## 다음 단계

1. **문서 읽기**
   - [README.md](./README.md) - 전체 기능 설명
   - [ARCHITECTURE.md](./ARCHITECTURE.md) - 상세 아키텍처

2. **커스터마이징**
   - 프롬프트 수정: `backend/app/agents/nodes.py`
   - UI 테마 변경: `frontend/src/App.tsx`
   - Mock 데이터 수정: `backend/app/services/`

3. **프로덕션 배포**
   - Docker 컨테이너화
   - 환경별 설정 분리
   - 모니터링 설정

## 도움이 필요하신가요?

- 이슈 생성: GitHub Issues
- 내부 문의: Slack #chatbot-support
- 문서: 프로젝트 루트의 *.md 파일들

즐거운 테스트 되세요! 🚀
