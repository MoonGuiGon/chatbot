"""
LLM Service - 사내 LLM API 연동
"""
import requests
import json
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator
import logging
import asyncio
import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """사내 LLM API 서비스 (OpenAI 호환)"""

    def __init__(self):
        # Chat Model (대화용)
        self.chat_api_key = settings.chat_api_key
        self.chat_api_url = settings.chat_api_url
        self.chat_model_name = settings.chat_model_name

        # Embedding Model (벡터 임베딩용)
        self.embedding_api_key = settings.embedding_api_key
        self.embedding_api_url = settings.embedding_api_url
        self.embedding_model_name = settings.embedding_model_name

        # Vision Model (이미지 분석용)
        self.vision_api_key = settings.vision_api_key
        self.vision_api_url = settings.vision_api_url
        self.vision_model_name = settings.vision_model_name

        # Mock 모드 체크
        self.use_mock_chat = not self.chat_api_key or not self.chat_api_url
        self.use_mock_embedding = not self.embedding_api_key or not self.embedding_api_url
        self.use_mock_vision = not self.vision_api_key or not self.vision_api_url

        if self.use_mock_chat or self.use_mock_embedding or self.use_mock_vision:
            logger.info("Some LLM APIs not configured. Using mock responses where needed.")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Any:
        """Chat completion (대화용)"""
        if self.use_mock_chat:
            return self._mock_completion(messages, stream)

        headers = {
            "Authorization": f"Bearer {self.chat_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.chat_model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        try:
            if stream:
                return self._stream_completion(self.chat_api_url, headers, data)
            else:
                response = requests.post(
                    f"{self.chat_api_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Chat API error: {e}")
            return self._mock_completion(messages, stream)

    def _stream_completion(self, api_url: str, headers: Dict, data: Dict) -> Iterator[str]:
        """Stream completion"""
        try:
            response = requests.post(
                f"{api_url}/chat/completions",
                headers=headers,
                json=data,
                stream=True,
                timeout=120
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield "죄송합니다. 응답 생성 중 오류가 발생했습니다."

    def _mock_completion(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        """Mock completion for testing"""
        user_message = messages[-1]['content'] if messages else ""

        mock_response = f"""질문에 대한 답변입니다: {user_message}

**분석 결과:**
- 부품 정보를 MongoDB에서 조회했습니다.
- 관련 문서 3개를 VectorDB에서 찾았습니다.
- 재고 정보: 현재 150개 보유중

**권장 사항:**
1. 최소 재고량 50개 유지 필요
2. 정기 점검 필요
3. 공급업체와 재계약 검토

출처: [문서A.pdf], [MongoDB: MAT-001]
"""

        if stream:
            return self._mock_stream(mock_response)
        else:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": mock_response
                    }
                }]
            }

    def _mock_stream(self, text: str) -> Iterator[str]:
        """Mock streaming"""
        import time
        words = text.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            time.sleep(0.05)  # Simulate streaming delay

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get text embedding (임베딩용)"""
        if self.use_mock_embedding:
            # Return mock embedding (768 dimensions)
            import random
            return [random.random() for _ in range(768)]

        headers = {
            "Authorization": f"Bearer {self.embedding_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.embedding_model_name,
            "input": text
        }

        try:
            response = requests.post(
                f"{self.embedding_api_url}/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Embedding API error: {e}")
            return None


# Global instance
llm_service = LLMService()
