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
        self.api_key = settings.llm_api_key
        self.api_url = settings.llm_api_url
        self.model_name = settings.llm_model_name
        self.embedding_model = settings.llm_embedding_model
        self.vision_model = settings.llm_vision_model
        self.use_mock = not self.api_key or not self.api_url

        if self.use_mock:
            logger.info("LLM API not configured. Using mock responses.")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Any:
        """Chat completion"""
        if self.use_mock:
            return self._mock_completion(messages, stream)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        try:
            if stream:
                return self._stream_completion(headers, data)
            else:
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._mock_completion(messages, stream)

    def _stream_completion(self, headers: Dict, data: Dict) -> Iterator[str]:
        """Stream completion"""
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
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
        """Get text embedding"""
        if self.use_mock:
            # Return mock embedding (768 dimensions)
            import random
            return [random.random() for _ in range(768)]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.embedding_model,
            "input": text
        }

        try:
            response = requests.post(
                f"{self.api_url}/embeddings",
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
