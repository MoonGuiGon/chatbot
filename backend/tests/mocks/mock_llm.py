"""
테스트용 Mock LLM
실제 LLM 없이도 개발 및 테스트 가능
"""
import json
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MockMessage:
    content: str
    role: str = "assistant"


@dataclass
class MockChatResponse:
    content: str

    @property
    def message(self):
        return MockMessage(content=self.content)


class MockChatLLM:
    """Mock Chat LLM - 사내 Chat LLM 대체"""

    def __init__(self, model: str = "mock-gpt-4", temperature: float = 0.1):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt: str) -> MockChatResponse:
        """프롬프트에 따라 적절한 응답 생성"""
        time.sleep(0.5)  # 실제 API 호출처럼 지연 시뮬레이션

        # Query Classification 응답
        if "분류하세요" in prompt or "classify" in prompt.lower():
            return self._classify_query(prompt)

        # 일반 답변 생성
        if "부품" in prompt or "재고" in prompt:
            return self._generate_parts_response(prompt)

        if "표" in prompt or "그래프" in prompt:
            return self._generate_table_response(prompt)

        return MockChatResponse(
            content="Mock LLM 응답입니다. 실제 환경에서는 사내 LLM이 답변합니다."
        )

    def _classify_query(self, prompt: str) -> MockChatResponse:
        """쿼리 분류 Mock 응답"""
        classification = {
            "intent": "part_search",
            "data_sources": ["mongodb", "vectordb"],
            "entities": {
                "part_numbers": ["ABC-12345"],
                "part_names": ["반도체 칩 A"],
                "date_ranges": [],
                "metrics": ["재고"]
            },
            "requires_calculation": False,
            "response_format": "mixed"
        }
        return MockChatResponse(content=json.dumps(classification, ensure_ascii=False))

    def _generate_parts_response(self, prompt: str) -> MockChatResponse:
        """부품 관련 응답 생성"""
        response = """
부품 ABC-12345 (반도체 칩 A)의 현재 재고 정보를 안내드립니다:

**재고 현황**
- 총 재고: 1,000개
- 가용 재고: 850개
- 예약: 150개
- 상태: 정상

**최근 출고 이력 (표)**

| 날짜 | 수량 | 목적지 | 담당자 |
|------|------|---------|--------|
| 2024-01-15 | 100개 | 라인 1 | 김철수 |
| 2024-01-10 | 50개 | 라인 2 | 이영희 |
| 2024-01-05 | 75개 | 라인 1 | 박민수 |

**장착 현황**
- 장비 EQ-001: 활성 (가동률 95%)
- 장비 EQ-002: 활성 (가동률 88%)

**월별 재고 추이 (그래프)**
```json
{
  "type": "line",
  "title": "최근 6개월 재고 추이",
  "data": {
    "labels": ["7월", "8월", "9월", "10월", "11월", "12월"],
    "datasets": [{
      "label": "재고량",
      "data": [950, 920, 880, 900, 920, 850]
    }]
  }
}
```

출처:
1. 부품 재고 관리 시스템 (MongoDB)
2. 부품 매뉴얼 v2.0 (PDF, 5페이지)
3. 출고 이력 데이터베이스
"""
        return MockChatResponse(content=response)

    def _generate_table_response(self, prompt: str) -> MockChatResponse:
        """표/그래프 포함 응답 생성"""
        response = """
부품별 재고 현황을 표로 정리했습니다:

| 부품번호 | 부품명 | 총 재고 | 가용 재고 | 예약 | 상태 |
|---------|--------|---------|-----------|------|------|
| ABC-12345 | 반도체 칩 A | 1,000 | 850 | 150 | 정상 |
| ABC-12346 | 반도체 칩 B | 500 | 450 | 50 | 정상 |
| ABC-12347 | 반도체 칩 C | 200 | 50 | 150 | 부족 |

**그래프 데이터**
```json
{
  "type": "bar",
  "title": "부품별 재고 현황",
  "data": {
    "labels": ["칩 A", "칩 B", "칩 C"],
    "datasets": [{
      "label": "가용 재고",
      "data": [850, 450, 50]
    }, {
      "label": "예약",
      "data": [150, 50, 150]
    }]
  }
}
```

출처: 부품 재고 관리 시스템
"""
        return MockChatResponse(content=response)


class MockEmbeddingLLM:
    """Mock Embedding LLM - 사내 Embedding LLM 대체"""

    def __init__(self, model: str = "mock-embedding"):
        self.model = model
        self.dimension = 1536  # OpenAI embedding 차원

    def embed_query(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환 (Mock)"""
        time.sleep(0.2)
        # 실제로는 랜덤이지만 같은 텍스트는 같은 벡터 반환
        random.seed(hash(text) % (2**32))
        return [random.random() for _ in range(self.dimension)]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 벡터로 변환"""
        return [self.embed_query(text) for text in texts]


class MockVisionLLM:
    """Mock Vision LLM - 사내 Vision LLM 대체"""

    def __init__(self, model: str = "mock-gpt-4-vision"):
        self.model = model

    def analyze_image(self, image_path: str, prompt: str = "") -> Dict[str, Any]:
        """이미지 분석 (Mock)"""
        time.sleep(1.0)

        # 파일 타입에 따라 다른 응답
        if "table" in image_path.lower() or "표" in image_path:
            return {
                "type": "table",
                "description": "부품 사양 비교표",
                "extracted_data": {
                    "headers": ["부품번호", "전압", "전류", "온도범위"],
                    "rows": [
                        ["ABC-12345", "3.3V", "0.5A", "-40~85°C"],
                        ["ABC-12346", "5.0V", "0.8A", "-20~70°C"]
                    ]
                }
            }

        if "graph" in image_path.lower() or "chart" in image_path.lower():
            return {
                "type": "graph",
                "description": "월별 부품 소비량 추이 그래프",
                "chart_type": "line",
                "data": {
                    "x_axis": ["1월", "2월", "3월", "4월", "5월"],
                    "y_axis": [120, 150, 130, 180, 200],
                    "unit": "개"
                }
            }

        return {
            "type": "image",
            "description": "반도체 부품 다이어그램",
            "details": "부품의 내부 구조와 핀 배치를 보여주는 다이어그램"
        }


class MockLLMFactory:
    """Mock LLM 팩토리 - 테스트 모드에서 사용"""

    @staticmethod
    def create_chat_llm(config: Any) -> MockChatLLM:
        """Chat LLM 생성"""
        return MockChatLLM(
            model=config.llm.chat_model,
            temperature=config.llm.temperature
        )

    @staticmethod
    def create_embedding_llm(config: Any) -> MockEmbeddingLLM:
        """Embedding LLM 생성"""
        return MockEmbeddingLLM(model=config.llm.embedding_model)

    @staticmethod
    def create_vision_llm(config: Any) -> MockVisionLLM:
        """Vision LLM 생성"""
        return MockVisionLLM(model=config.llm.vision_model)
