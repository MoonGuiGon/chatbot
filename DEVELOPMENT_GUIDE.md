# 개발 가이드

## PM 관점에서 본 시스템 설계 요약

### 요구사항 충족도

#### ✅ 완전히 구현된 기능
1. **RAG 시스템**
   - MongoDB (부품 정보) + pgvector (문서) 통합 검색
   - 쿼리 분석을 통한 자동 데이터 소스 선택
   - Hallucination 최소화 (출처 강제, 신뢰도 점수)

2. **문서 처리**
   - 다중 포맷 지원 (PDF, PPT, Excel, Word)
   - 사용자 검수 시스템
   - 메타데이터 관리

3. **피드백 및 학습**
   - 사용자 피드백 수집
   - 피드백 기반 개선 제안
   - Few-shot Learning 준비

4. **커스터마이징**
   - Model, Temperature 선택
   - Custom Prompt 지원

5. **UX**
   - 진행 상황 실시간 표시
   - 표/그래프 렌더링 (Recharts)
   - 출처 제공 및 다운로드

#### 🚧 추가 개발 필요
1. **Vision API 통합**
   - 현재: 구조만 구현
   - 필요: 실제 사내 Vision API 연동

2. **스트리밍 응답**
   - 현재: SSE 엔드포인트 구현
   - 필요: LLM 스트리밍 통합

3. **고급 문서 처리**
   - 현재: 기본 파싱
   - 필요: Semantic Chunking, 이미지 추출 고도화

## 개발 단계별 가이드

### Phase 1: 테스트 환경 실행 (지금 바로 가능)

```bash
# 1. 저장소 클론 또는 이동
cd /Users/mungyugon/work/git/chatbot

# 2. 테스트 모드로 실행
./start_test.sh

# 3. 브라우저에서 접속
# http://localhost:3000

# 4. 테스트 질문
- "부품 ABC-12345의 재고는?"
- "반도체 칩 A의 출고 이력을 알려줘"
- "부품 검사 절차가 뭐야?"

# 5. 종료
./stop_test.sh
```

### Phase 2: 실제 DB/LLM 연동

#### 2.1 MongoDB 설정
```bash
# MongoDB 실행
mongod --port 27017

# 초기 데이터 임포트 (부품 정보)
# backend/tests/mocks/mock_db.py의 _init_parts_data() 참조
```

#### 2.2 PostgreSQL + pgvector 설정
```bash
# PostgreSQL 설치 및 실행
brew install postgresql
brew services start postgresql

# pgvector extension 설치
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# 데이터베이스 생성
createdb vectordb
psql vectordb -c "CREATE EXTENSION vector;"
```

#### 2.3 사내 LLM 연동
```bash
# .env 파일 수정
TEST_MODE=False

# 실제 API 정보 입력
LLM_API_KEY=your-real-api-key
LLM_CHAT_URL=https://common.llm.com/v1/chat/completions
LLM_EMBEDDING_URL=https://embedding.llm.com/v1/embeddings
LLM_VISION_URL=https://vision.llm.com/v1/chat/completions
```

### Phase 3: Vision API 통합

#### Vision API 활용 시나리오
1. **표 이미지 → 텍스트 변환**
2. **그래프 → 데이터 추출**
3. **다이어그램 → 설명 생성**

#### 구현 위치
- `backend/app/services/llm_service.py` - `RealVisionLLM.analyze_image()`
- `backend/app/services/document_processor.py` - 이미지 추출 로직

```python
# Vision API 호출 예시
def analyze_image(self, image_path: str, prompt: str = ""):
    import base64

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = self.llm.invoke([
        {
            "type": "text",
            "text": prompt or "이미지를 분석하세요"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}"
            }
        }
    ])

    return response
```

### Phase 4: 성능 최적화

#### 4.1 캐시 시스템 구현
```python
# backend/app/services/cache_service.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379)

def cache_query(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(query, *args, **kwargs):
            cache_key = f"query:{hash(query)}"
            cached = redis_client.get(cache_key)

            if cached:
                return json.loads(cached)

            result = func(query, *args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### 4.2 Re-ranking 구현
```python
# Semantic Search + Re-ranking
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, documents, top_k=5):
    pairs = [[query, doc['content']] for doc in documents]
    scores = cross_encoder.predict(pairs)

    # 점수로 정렬
    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, _ in ranked[:top_k]]
```

### Phase 5: Frontend 고도화

#### 5.1 문서 업로드 UI
```jsx
// frontend/src/components/Document/DocumentUpload.jsx
import { useDropzone } from 'react-dropzone';

const DocumentUpload = () => {
  const onDrop = async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      const result = await documentAPI.uploadDocument(file);
      // 검수 UI로 이동
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-powerpoint': ['.ppt', '.pptx'],
      'application/msword': ['.doc', '.docx'],
      'application/vnd.ms-excel': ['.xls', '.xlsx']
    }
  });

  return (
    <Box {...getRootProps()}>
      <input {...getInputProps()} />
      <Typography>파일을 드래그하거나 클릭하세요</Typography>
    </Box>
  );
};
```

#### 5.2 Settings Dialog
```jsx
// frontend/src/components/Settings/SettingsDialog.jsx
const SettingsDialog = ({ open, onClose }) => {
  const { settings, updateSettings } = useChatStore();

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>설정</DialogTitle>
      <DialogContent>
        <FormControl fullWidth>
          <InputLabel>모델</InputLabel>
          <Select
            value={settings.model}
            onChange={(e) => updateSettings({ model: e.target.value })}
          >
            <MenuItem value="gpt-4">GPT-4</MenuItem>
            <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
          </Select>
        </FormControl>

        <Typography gutterBottom>Temperature: {settings.temperature}</Typography>
        <Slider
          value={settings.temperature}
          onChange={(e, v) => updateSettings({ temperature: v })}
          min={0}
          max={1}
          step={0.1}
        />

        <TextField
          fullWidth
          multiline
          rows={4}
          label="Custom Prompt"
          value={settings.customPrompt}
          onChange={(e) => updateSettings({ customPrompt: e.target.value })}
        />
      </DialogContent>
    </Dialog>
  );
};
```

## 코드 수정 가이드

### 새로운 LangGraph 노드 추가

#### 1. 노드 구현
```python
# backend/app/agents/nodes.py
class NewNode:
    @staticmethod
    def execute(state: GraphState) -> GraphState:
        # 노드 로직
        state["new_field"] = "value"
        return state
```

#### 2. 워크플로우에 추가
```python
# backend/app/agents/chatbot_agent.py
workflow.add_node("new_node", NewNode.execute)
workflow.add_edge("previous_node", "new_node")
workflow.add_edge("new_node", "next_node")
```

### 새로운 API 엔드포인트 추가

```python
# backend/app/routes/new_route.py
from flask import Blueprint

bp = Blueprint("new_route", __name__)

@bp.route("/api/new", methods=["POST"])
def new_endpoint():
    # 로직
    return jsonify({"success": True})

# backend/app/__init__.py
from app.routes import new_route
app.register_blueprint(new_route.bp)
```

### Frontend 새로운 컴포넌트 추가

```jsx
// frontend/src/components/NewComponent.jsx
import React from 'react';
import { Box } from '@mui/material';

const NewComponent = () => {
  return (
    <Box>
      New Component
    </Box>
  );
};

export default NewComponent;

// App.jsx에서 사용
import NewComponent from './components/NewComponent';
```

## 트러블슈팅

### 1. Backend 서버가 시작되지 않음

**증상**: `ModuleNotFoundError` 또는 `ImportError`

**해결**:
```bash
# 가상환경 재생성
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend 빌드 오류

**증상**: `Cannot find module` 에러

**해결**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 3. Mock LLM 응답 커스터마이징

**파일**: `backend/tests/mocks/mock_llm.py`

```python
# 특정 질문에 대한 응답 추가
def invoke(self, prompt: str):
    if "특정 질문" in prompt:
        return MockChatResponse(content="커스텀 응답")
    # ...
```

### 4. Mock 데이터 추가

**파일**: `backend/tests/mocks/mock_db.py`

```python
def _init_parts_data(self):
    return [
        {
            "_id": "part_004",
            "part_number": "NEW-12345",
            # ... 새로운 부품 데이터
        }
    ]
```

## 배포 가이드

### Docker 컨테이너화 (향후 추가)

```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "run.py"]

# Dockerfile (Frontend)
FROM node:18-alpine
WORKDIR /app
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build
CMD ["npm", "run", "preview"]
```

### 환경별 설정 관리

```bash
# 개발 환경
.env.development

# 스테이징 환경
.env.staging

# 운영 환경
.env.production
```

## 모니터링 및 로깅 (향후 추가)

### 로깅 설정
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 메트릭 수집
```python
# Prometheus + Grafana 연동
from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
response_time = Histogram('response_time_seconds', 'Response time')
```

## 다음 단계

1. **즉시 테스트**: `./start_test.sh` 실행
2. **DB 연동**: MongoDB, PostgreSQL 설정
3. **Vision API**: 사내 Vision API 통합
4. **성능 테스트**: 대량 데이터로 부하 테스트
5. **사용자 테스트**: 실제 부품 데이터로 검증

## 기술 지원

- **이슈 트래킹**: GitHub Issues
- **문서**: README.md, ARCHITECTURE.md
- **코드 리뷰**: PR 필수

---

**구현 완료일**: 2025-11-08
**개발자**: Claude Code (PM 모드)
**상태**: 테스트 준비 완료 ✅
