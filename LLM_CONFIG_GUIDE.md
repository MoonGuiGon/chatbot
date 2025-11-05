# LLM API 설정 가이드

## 개요

이 챗봇은 **3가지 다른 LLM 모델**을 사용합니다. 각 모델은 서로 다른 용도로 사용되며, 각각 다른 API URL과 모델명을 가질 수 있습니다.

---

## 3가지 LLM 모델

### 1. **Chat Model** (대화 생성용)

**용도**: 사용자와의 대화 응답 생성

**사용 예시**:
- 사용자 질문에 대한 답변 생성
- 문서 요약 및 분석 결과 텍스트 생성
- 재고 분석 보고서 작성

**API 호출 위치**:
- `app/services/llm_service.py` → `chat_completion()` 함수
- `app/agents/chatbot_agent.py` → 응답 생성 노드

**필요 설정**:
```bash
CHAT_API_KEY=sk-xxx...
CHAT_API_URL=https://api.openai.com/v1
CHAT_MODEL_NAME=gpt-4
```

---

### 2. **Embedding Model** (벡터 임베딩용)

**용도**: 텍스트를 벡터로 변환하여 유사도 검색

**사용 예시**:
- 사용자 질문을 벡터로 변환
- 문서를 벡터로 변환하여 pgvector에 저장
- 유사한 문서 검색 (RAG)

**API 호출 위치**:
- `app/services/llm_service.py` → `get_embedding()` 함수
- `app/services/pgvector_service.py` → 문서 검색
- `app/services/document_processor.py` → 문서 처리

**필요 설정**:
```bash
EMBEDDING_API_KEY=sk-xxx...
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL_NAME=text-embedding-3-large
```

---

### 3. **Vision Model** (이미지 분석용)

**용도**: 문서 스크린샷 및 이미지 분석

**사용 예시**:
- PDF 문서의 스크린샷 분석
- 차트, 그래프, 다이어그램 해석
- 표(테이블) 데이터 추출
- 이미지 속 텍스트 읽기 (OCR)

**API 호출 위치**:
- `app/services/vision_service.py` → `analyze_document_image()` 함수
- `app/services/document_processor.py` → 문서 스크린샷 분석

**필요 설정**:
```bash
VISION_API_KEY=sk-xxx...
VISION_API_URL=https://api.openai.com/v1
VISION_MODEL_NAME=gpt-4-vision-preview
```

---

## 설정 방법

### 1. `.env` 파일 생성

```bash
cd backend
cp .env.example .env
nano .env  # 또는 원하는 에디터로 편집
```

### 2. 각 모델 API 정보 입력

#### 예시 1: OpenAI API 사용

```bash
# Chat Model
CHAT_API_KEY=sk-your-openai-key
CHAT_API_URL=https://api.openai.com/v1
CHAT_MODEL_NAME=gpt-4

# Embedding Model
EMBEDDING_API_KEY=sk-your-openai-key
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL_NAME=text-embedding-3-large

# Vision Model
VISION_API_KEY=sk-your-openai-key
VISION_API_URL=https://api.openai.com/v1
VISION_MODEL_NAME=gpt-4-vision-preview
```

#### 예시 2: 사내 LLM API 사용

```bash
# Chat Model (사내 대화 모델)
CHAT_API_KEY=internal-key-001
CHAT_API_URL=https://llm.company.com/api/v1
CHAT_MODEL_NAME=company-chat-model-v2

# Embedding Model (사내 임베딩 모델)
EMBEDDING_API_KEY=internal-key-002
EMBEDDING_API_URL=https://embedding.company.com/api/v1
EMBEDDING_MODEL_NAME=company-embedding-model-v1

# Vision Model (사내 비전 모델)
VISION_API_KEY=internal-key-003
VISION_API_URL=https://vision.company.com/api/v1
VISION_MODEL_NAME=company-vision-model-v1
```

#### 예시 3: 혼합 사용 (Chat은 OpenAI, Embedding은 사내, Vision은 Anthropic)

```bash
# Chat Model - OpenAI GPT-4
CHAT_API_KEY=sk-openai-key
CHAT_API_URL=https://api.openai.com/v1
CHAT_MODEL_NAME=gpt-4

# Embedding Model - 사내 모델
EMBEDDING_API_KEY=internal-embedding-key
EMBEDDING_API_URL=https://company-embed.com/api
EMBEDDING_MODEL_NAME=custom-embedding-768

# Vision Model - Anthropic Claude
VISION_API_KEY=sk-anthropic-key
VISION_API_URL=https://api.anthropic.com/v1
VISION_MODEL_NAME=claude-3-opus-20240229
```

### 3. 서버 재시작

```bash
python run.py
```

---

## API 엔드포인트 형식

각 API는 **OpenAI 호환 형식**을 따라야 합니다.

### Chat Model API

**엔드포인트**: `POST {CHAT_API_URL}/chat/completions`

**요청 형식**:
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "안녕하세요"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**응답 형식**:
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "안녕하세요! 무엇을 도와드릴까요?"
      }
    }
  ]
}
```

### Embedding Model API

**엔드포인트**: `POST {EMBEDDING_API_URL}/embeddings`

**요청 형식**:
```json
{
  "model": "text-embedding-3-large",
  "input": "임베딩할 텍스트"
}
```

**응답 형식**:
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ..., 0.768]
    }
  ]
}
```

### Vision Model API

**엔드포인트**: `POST {VISION_API_URL}/chat/completions`

**요청 형식**:
```json
{
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "이 이미지를 분석해주세요"},
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgo..."
          }
        }
      ]
    }
  ]
}
```

---

## Mock 모드

API 설정이 없으면 자동으로 **Mock 모드**로 작동합니다.

**Mock 모드 특징**:
- 실제 API 호출 없이 테스트 데이터 반환
- 개발 및 테스트 용도
- 비용 없이 시스템 동작 확인 가능

**활성화 조건**:
- `CHAT_API_KEY` 또는 `CHAT_API_URL`이 비어있으면 → Chat Mock 모드
- `EMBEDDING_API_KEY` 또는 `EMBEDDING_API_URL`이 비어있으면 → Embedding Mock 모드
- `VISION_API_KEY` 또는 `VISION_API_URL`이 비어있으면 → Vision Mock 모드

---

## 트러블슈팅

### Q: 서버가 실행되지만 API 호출이 실패합니다

**확인사항**:
1. `.env` 파일이 `backend/` 디렉토리에 있는지 확인
2. API Key가 올바른지 확인
3. API URL 끝에 `/v1`이 있는지 확인 (OpenAI 형식)
4. 모델명이 정확한지 확인

**로그 확인**:
```bash
# 서버 로그에서 에러 확인
python run.py
# "Chat API error:", "Embedding API error:", "Vision API error:" 확인
```

### Q: 일부 모델만 설정하고 싶습니다

**가능합니다!** 예를 들어:
- Chat과 Embedding만 설정하고 Vision은 Mock 모드로 사용
- 각 모델을 독립적으로 설정 가능

```bash
# Chat과 Embedding만 설정
CHAT_API_KEY=sk-xxx
CHAT_API_URL=https://api.openai.com/v1
CHAT_MODEL_NAME=gpt-4

EMBEDDING_API_KEY=sk-xxx
EMBEDDING_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL_NAME=text-embedding-3-large

# Vision은 설정 안 함 (Mock 모드로 작동)
VISION_API_KEY=
VISION_API_URL=
VISION_MODEL_NAME=
```

### Q: 모델을 바꾸고 싶습니다

1. `.env` 파일에서 모델명 변경
2. 서버 재시작

```bash
# 예: GPT-4 → GPT-3.5로 변경
CHAT_MODEL_NAME=gpt-3.5-turbo
```

---

## 비용 최적화 팁

### 1. 모델 선택

**저비용 옵션**:
- Chat: `gpt-3.5-turbo` (빠르고 저렴)
- Embedding: `text-embedding-ada-002` (저렴)
- Vision: Mock 모드 (무료) 또는 필요시에만 활성화

**고성능 옵션**:
- Chat: `gpt-4` 또는 `gpt-4-turbo`
- Embedding: `text-embedding-3-large`
- Vision: `gpt-4-vision-preview`

### 2. 캐싱 활용

- Embedding은 Redis 캐시에 저장됨
- 동일한 텍스트는 재계산 안 함
- 비용 절감 효과

### 3. 모델 분리 활용

- 중요하지 않은 작업은 저렴한 모델 사용
- Vision 모델은 필요할 때만 활성화
- 각 모델을 용도에 맞게 최적화

---

## 요약

✅ **3가지 모델 분리 설정**:
- Chat Model (대화)
- Embedding Model (벡터 변환)
- Vision Model (이미지 분석)

✅ **각각 다른 API 사용 가능**:
- URL, API Key, 모델명 모두 독립적

✅ **Mock 모드 지원**:
- API 없이도 테스트 가능
- 개발 환경에서 유용

✅ **비용 최적화**:
- 용도에 맞는 모델 선택
- 캐싱 활용

---

**문제가 있으면 로그를 확인하세요**:
```bash
python run.py
# 각 모델의 초기화 로그 확인
# "Chat API", "Embedding API", "Vision API" 관련 메시지 확인
```
