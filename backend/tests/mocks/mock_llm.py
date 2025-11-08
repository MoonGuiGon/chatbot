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

        # 출고 이력 관련 질문 (년도별 데이터)
        if "출고" in prompt and ("년" in prompt or "연도" in prompt or "2021" in prompt or "2022" in prompt):
            return self._generate_yearly_shipment_response(prompt)

        # 기본 재고 현황 표
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
      "data": [850, 450, 50],
      "backgroundColor": "rgba(54, 162, 235, 0.8)"
    }, {
      "label": "예약",
      "data": [150, 50, 150],
      "backgroundColor": "rgba(255, 206, 86, 0.8)"
    }]
  }
}
```

출처: 부품 재고 관리 시스템
"""
        return MockChatResponse(content=response)

    def _generate_yearly_shipment_response(self, prompt: str) -> MockChatResponse:
        """년도별 출고 데이터 표 및 그래프 생성"""
        response = """
부품 ABC-12345의 최근 3년간(2021-2023) 출고 데이터를 분석했습니다.

## 📊 연도별 출고 현황 요약

### 총 출고량
- **2021년**: 12,450개
- **2022년**: 15,800개 (전년 대비 +26.9%)
- **2023년**: 18,200개 (전년 대비 +15.2%)

---

## 📅 월별 출고 이력 (2021-2023)

| 월 | 2021년 | 2022년 | 2023년 | 평균 |
|----|--------|--------|--------|------|
| 1월 | 950개 | 1,200개 | 1,450개 | 1,200개 |
| 2월 | 880개 | 1,150개 | 1,380개 | 1,137개 |
| 3월 | 1,020개 | 1,280개 | 1,520개 | 1,273개 |
| 4월 | 1,050개 | 1,320개 | 1,550개 | 1,307개 |
| 5월 | 1,100개 | 1,400개 | 1,620개 | 1,373개 |
| 6월 | 1,080개 | 1,380개 | 1,580개 | 1,347개 |
| 7월 | 990개 | 1,250개 | 1,480개 | 1,240개 |
| 8월 | 920개 | 1,180개 | 1,420개 | 1,173개 |
| 9월 | 1,040개 | 1,340개 | 1,590개 | 1,323개 |
| 10월 | 1,100개 | 1,420개 | 1,650개 | 1,390개 |
| 11월 | 1,150개 | 1,480개 | 1,710개 | 1,447개 |
| 12월 | 1,170개 | 1,400개 | 1,750개 | 1,440개 |
| **합계** | **12,450개** | **15,800개** | **18,200개** | **15,483개** |

---

## 🏭 라인별 출고 비율 (2023년 기준)

| 라인 | 출고량 | 비율 | 주요 용도 |
|------|--------|------|-----------|
| 라인 1 | 7,280개 | 40% | 주력 생산 라인 |
| 라인 2 | 5,460개 | 30% | 보조 생산 라인 |
| 라인 3 | 3,640개 | 20% | 테스트/검증 |
| 기타 | 1,820개 | 10% | 유지보수/예비 |
| **합계** | **18,200개** | **100%** | - |

---

## 📈 3년간 출고 추이 그래프

```json
{
  "type": "line",
  "title": "월별 출고 추이 (2021-2023)",
  "data": {
    "labels": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
    "datasets": [
      {
        "label": "2021년",
        "data": [950, 880, 1020, 1050, 1100, 1080, 990, 920, 1040, 1100, 1150, 1170],
        "borderColor": "rgba(75, 192, 192, 1)",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "tension": 0.4
      },
      {
        "label": "2022년",
        "data": [1200, 1150, 1280, 1320, 1400, 1380, 1250, 1180, 1340, 1420, 1480, 1400],
        "borderColor": "rgba(54, 162, 235, 1)",
        "backgroundColor": "rgba(54, 162, 235, 0.2)",
        "tension": 0.4
      },
      {
        "label": "2023년",
        "data": [1450, 1380, 1520, 1550, 1620, 1580, 1480, 1420, 1590, 1650, 1710, 1750],
        "borderColor": "rgba(255, 99, 132, 1)",
        "backgroundColor": "rgba(255, 99, 132, 0.2)",
        "tension": 0.4
      }
    ]
  }
}
```

---

## 📊 연도별 총 출고량 비교 (막대 그래프)

```json
{
  "type": "bar",
  "title": "연도별 총 출고량",
  "data": {
    "labels": ["2021년", "2022년", "2023년"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [12450, 15800, 18200],
      "backgroundColor": [
        "rgba(75, 192, 192, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 99, 132, 0.8)"
      ],
      "borderColor": [
        "rgba(75, 192, 192, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 99, 132, 1)"
      ],
      "borderWidth": 2
    }]
  }
}
```

---

## 🎯 라인별 출고 비율 (파이 차트)

```json
{
  "type": "pie",
  "title": "라인별 출고 비율 (2023년)",
  "data": {
    "labels": ["라인 1 (40%)", "라인 2 (30%)", "라인 3 (20%)", "기타 (10%)"],
    "datasets": [{
      "data": [7280, 5460, 3640, 1820],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(75, 192, 192, 0.8)"
      ],
      "borderColor": [
        "rgba(255, 99, 132, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 206, 86, 1)",
        "rgba(75, 192, 192, 1)"
      ],
      "borderWidth": 2
    }]
  }
}
```

---

## 💡 주요 인사이트

1. **지속적인 성장세**: 2021년 대비 2023년 46.2% 증가
2. **성수기**: 10-12월 출고량이 가장 많음 (평균 대비 +15%)
3. **비수기**: 2월, 8월 출고량 감소 경향 (설 연휴, 휴가 시즌)
4. **라인 1 집중도**: 전체 출고의 40%가 라인 1에 집중
5. **안정적 수요**: 매년 평균 12-15% 성장률 유지

---

**출처:**
1. 부품 출고 관리 시스템 (MongoDB)
2. 생산 라인 운영 데이터베이스
3. 2021-2023 연간 생산 보고서 (PDF)
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
