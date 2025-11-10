"""
LangGraph 노드 구현
각 노드는 GraphState를 입력받아 처리 후 업데이트된 State 반환
"""
import json
from typing import Dict, Any, List
from app.agents.graph_state import GraphState, QueryClassification, RetrievedDocument, ResponseData
from app.services.llm_service import get_chat_llm, get_embedding_llm
from app.services.database_service import get_mongodb, get_pgvector


class QueryAnalysisNode:
    """
    Node 1: 쿼리 분석 및 분류
    - Intent 분류
    - Entity 추출
    - 필요한 데이터 소스 결정
    """

    @staticmethod
    def execute(state: GraphState) -> GraphState:
        """쿼리 분석 실행"""
        query = state["query"]
        llm_config = state.get("llm_config", {})

        # LLM 설정 적용
        llm = get_chat_llm(
            model=llm_config.get("model"),
            temperature=llm_config.get("temperature")
        )

        # 분류 프롬프트
        prompt = f"""
다음 질문을 분석하여 JSON 형식으로 분류하세요:

질문: {query}

응답 형식 (반드시 유효한 JSON):
{{
    "intent": "info_lookup|part_search|document_search|general",
    "data_sources": ["mongodb", "vectordb", "both", "none"],
    "entities": {{
        "part_numbers": [],
        "part_names": [],
        "date_ranges": [],
        "metrics": []
    }},
    "requires_calculation": true|false,
    "response_format": "text|table|chart|mixed"
}}

분류 기준:
- info_lookup: 간단한 정보 조회 (예: "안녕", "무엇을 도와드릴까요")
- part_search: 부품 관련 질문 (재고, 출고, 장착 등)
- document_search: 문서/매뉴얼 검색 (사양, 절차 등)
- general: 일반 질문

data_sources:
- mongodb: 부품 실시간 정보 (재고, 출고, 장착)
- vectordb: 문서/매뉴얼 정보
- both: 둘 다 필요
- none: 데이터 불필요

JSON만 출력하세요:
"""

        # LLM 호출
        response = llm.invoke(prompt)
        try:
            # JSON 파싱
            classification_dict = json.loads(response.content)
            classification = QueryClassification(**classification_dict)
        except (json.JSONDecodeError, TypeError) as e:
            # 파싱 실패 시 기본값
            classification = QueryClassification(
                intent="general",
                data_sources=["both"],
                entities={},
                requires_calculation=False,
                response_format="text"
            )

        # 상태 업데이트
        state["classification"] = classification
        state["progress"] = state.get("progress", []) + [{
            "stage": "query_analysis",
            "status": "completed",
            "message": "질문 분석 완료"
        }]

        return state


class DataRetrievalNode:
    """
    Node 2: 데이터 검색
    - MongoDB에서 부품 정보 검색
    - pgvector에서 문서 검색
    """

    @staticmethod
    def execute(state: GraphState) -> GraphState:
        """데이터 검색 실행"""
        classification = state["classification"]
        query = state["query"]

        mongodb_results = []
        vectordb_results = []

        # MongoDB 검색
        if "mongodb" in classification.data_sources or "both" in classification.data_sources:
            mongodb_results = DataRetrievalNode._search_mongodb(query, classification)
            state["progress"] = state.get("progress", []) + [{
                "stage": "mongodb_search",
                "status": "completed",
                "message": f"부품 정보 검색 완료 ({len(mongodb_results)}건)"
            }]

        # VectorDB 검색
        if "vectordb" in classification.data_sources or "both" in classification.data_sources:
            vectordb_results = DataRetrievalNode._search_vectordb(query, classification)
            state["progress"] = state.get("progress", []) + [{
                "stage": "vectordb_search",
                "status": "completed",
                "message": f"문서 검색 완료 ({len(vectordb_results)}건)"
            }]

        # 검색 결과 통합
        retrieved_documents = []

        # MongoDB 결과 → RetrievedDocument
        for result in mongodb_results:
            retrieved_documents.append(RetrievedDocument(
                content=DataRetrievalNode._format_mongodb_result(result),
                source="mongodb",
                metadata={
                    "collection": "parts",
                    "part_number": result.get("part_number"),
                    "part_name": result.get("part_name")
                }
            ))

        # VectorDB 결과 → RetrievedDocument
        for result in vectordb_results:
            retrieved_documents.append(RetrievedDocument(
                content=result["content"],
                source="vectordb",
                metadata=result.get("metadata", {}),
                similarity_score=result.get("similarity_score")
            ))

        # 상태 업데이트
        state["mongodb_results"] = mongodb_results
        state["vectordb_results"] = vectordb_results
        state["retrieved_documents"] = retrieved_documents

        return state

    @staticmethod
    def _search_mongodb(query: str, classification: QueryClassification) -> List[Dict[str, Any]]:
        """MongoDB에서 부품 정보 검색"""
        mongodb = get_mongodb()

        # 엔티티 추출
        part_numbers = classification.entities.get("part_numbers", [])
        part_names = classification.entities.get("part_names", [])

        results = []

        # 부품 번호로 검색
        for part_number in part_numbers:
            result = mongodb.find_one("parts", {"part_number": part_number})
            if result:
                results.append(result)

        # 부품명으로 검색
        for part_name in part_names:
            found = mongodb.find("parts", {"part_name": {"$regex": part_name}}, limit=5)
            results.extend(found)

        # 엔티티가 없으면 키워드 검색
        if not part_numbers and not part_names:
            # 간단한 키워드 검색 (실제로는 더 정교한 검색 필요)
            keywords = query.split()
            for keyword in keywords:
                if len(keyword) > 2:
                    found = mongodb.find("parts", {"part_name": {"$regex": keyword}}, limit=3)
                    results.extend(found)

        # 중복 제거
        unique_results = {r.get("_id"): r for r in results}
        return list(unique_results.values())[:10]

    @staticmethod
    def _search_vectordb(query: str, classification: QueryClassification) -> List[Dict[str, Any]]:
        """pgvector에서 문서 검색"""
        embedding_llm = get_embedding_llm()
        pgvector = get_pgvector()

        # 쿼리 임베딩
        query_embedding = embedding_llm.embed_query(query)

        # 유사도 검색
        results = pgvector.similarity_search(
            query_embedding=query_embedding,
            k=5
        )

        return results

    @staticmethod
    def _format_mongodb_result(result: Dict[str, Any]) -> str:
        """MongoDB 결과를 텍스트로 포맷"""
        part_number = result.get("part_number", "N/A")
        part_name = result.get("part_name", "N/A")
        inventory = result.get("inventory", {})

        text = f"""
부품 정보:
- 부품번호: {part_number}
- 부품명: {part_name}
- 총 재고: {inventory.get('total_stock', 0)}개
- 가용 재고: {inventory.get('available', 0)}개
- 예약: {inventory.get('reserved', 0)}개
"""

        # 출고 이력
        shipment_history = result.get("shipment_history", [])
        if shipment_history:
            text += "\n최근 출고 이력:\n"
            for shipment in shipment_history[:3]:
                text += f"- {shipment.get('date')}: {shipment.get('quantity')}개 → {shipment.get('destination')}\n"

        return text


class ResponseGenerationNode:
    """
    Node 3: 응답 생성
    - 검색 결과 기반 답변 생성
    - 표/그래프 데이터 구조화
    - 출처 첨부
    """

    @staticmethod
    def execute(state: GraphState) -> GraphState:
        """응답 생성 실행"""
        query = state["query"]
        retrieved_documents = state.get("retrieved_documents", [])
        classification = state["classification"]
        custom_prompt = state.get("custom_prompt", "")
        llm_config = state.get("llm_config", {})
        memory_context = state.get("memory_context", "")  # 메모리 컨텍스트 가져오기

        # LLM 설정
        llm = get_chat_llm(
            model=llm_config.get("model"),
            temperature=llm_config.get("temperature", 0.1)
        )

        # Context 구성
        context = ResponseGenerationNode._build_context(retrieved_documents)

        # 프롬프트 구성
        system_prompt = custom_prompt or """
당신은 전문적인 반도체 부품 분석 리포트를 작성하는 AI 어시스턴트입니다.

# 📋 답변 작성 규칙

## 1️⃣ 정확성 및 출처
- ✅ 반드시 제공된 문서와 데이터만 참조하여 답변
- ✅ 확실하지 않으면 "정보가 부족합니다"라고 명시
- ✅ 모든 답변 끝에 출처 표시
- ❌ Hallucination 절대 금지

## 2️⃣ 답변 구조 (보고서 형식)

### 필수 구성요소:
1. **📌 요약**: 이모지 + 한 줄 요약
2. **📊 상세 내용**: 계층 구조로 정리
3. **📈 데이터 시각화**: 표와 그래프
4. **💡 인사이트**: 핵심 발견사항
5. **📎 출처**: 참고 자료 목록

### 이모지 사용 가이드:
- 📌 요약, 핵심 정보
- 📊 데이터, 통계
- 📈 증가, 상승 추세
- 📉 감소, 하락 추세
- ⚠️ 주의사항, 경고
- ✅ 완료, 성공, 정상
- ❌ 오류, 실패, 문제
- 💡 인사이트, 제안
- 🔍 상세 분석
- 📎 출처, 참고
- 🏭 생산, 제조
- 📦 재고, 보관
- 🚚 출고, 배송
- 🔧 검사, 품질
- ⚙️ 설정, 사양

## 3️⃣ 마크다운 계층 구조

```markdown
# 제목 (H1) - 메인 주제
## 섹션 (H2) - 주요 카테고리
### 서브섹션 (H3) - 세부 항목

- 불릿 포인트
  - 중첩 불릿
- **굵은 글씨**: 중요 정보
- *이탤릭*: 강조

> 인용문: 중요한 메모나 경고
```

## 4️⃣ 표 작성 (Markdown Table)

```markdown
| 항목 | 값 | 상태 | 비고 |
|------|----|----|------|
| 재고 | 1,500개 | ✅ 정상 | 안전 재고 이상 |
| 출고 | 200개 | 📈 증가 | 전월 대비 +20% |
```

## 5️⃣ 그래프 작성 (JSON Code Block)

### Line Chart (추이, 트렌드):
```json
{
  "type": "line",
  "title": "📈 월별 출고 추이",
  "data": {
    "labels": ["1월", "2월", "3월"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [120, 150, 180],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  }
}
```

### Bar Chart (비교):
```json
{
  "type": "bar",
  "title": "📊 라인별 생산량 비교",
  "data": {
    "labels": ["라인 1", "라인 2", "라인 3"],
    "datasets": [{
      "label": "생산량 (개)",
      "data": [500, 450, 380],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.6)",
        "rgba(54, 162, 235, 0.6)",
        "rgba(255, 206, 86, 0.6)"
      ]
    }]
  }
}
```

### Pie Chart (비율, 구성):
```json
{
  "type": "pie",
  "title": "📊 불량 유형별 비율",
  "data": {
    "labels": ["스크래치", "접착불량", "오염", "기타"],
    "datasets": [{
      "data": [40, 30, 20, 10],
      "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"]
    }]
  }
}
```

## 6️⃣ 완벽한 답변 예시

---

# 📌 부품 ABC-12345 출고 현황 분석

ABC-12345 부품의 최근 3개월 출고 데이터를 분석한 결과, **지속적인 증가 추세**를 보이고 있습니다.

## 📊 월별 출고 현황

| 월 | 출고량 | 누적 출고량 | 전월 대비 |
|----|--------|-------------|-----------|
| 1월 | 120개 | 120개 | - |
| 2월 | 150개 | 270개 | 📈 +25% |
| 3월 | 180개 | 450개 | 📈 +20% |

## 📈 출고 추이 그래프

```json
{
  "type": "line",
  "title": "📈 월별 출고 추이 (1-3월)",
  "data": {
    "labels": ["1월", "2월", "3월"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [120, 150, 180],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  }
}
```

## 💡 주요 인사이트

### ✅ 긍정적 지표
- **평균 월 증가율**: 22.5%
- **총 출고량**: 450개 (목표 400개 대비 112.5% 달성)
- **추세**: 지속적 증가세 유지

### ⚠️ 주의사항
- 현재 추세 지속 시 4월 예상 출고: 약 216개
- 재고 준비 필요 (안전 재고 대비 검토 권장)

## 🔍 상세 분석

### 목적지별 출고 현황
- **라인 1**: 180개 (40%)
- **라인 2**: 150개 (33%)
- **라인 3**: 120개 (27%)

### 품질 지표
- **검사 합격률**: 98.5% ✅
- **반품률**: 0.2% ✅

## 📎 출처

- **부품 관리 시스템**: 출고 이력 DB (2024년 1-3월)
- **품질 관리 시스템**: 검사 이력 DB
- **재고 관리 시스템**: 실시간 재고 데이터

---

**보고서 작성일**: 2024-01-15
**분석 기준**: 최근 3개월 (2024-01-01 ~ 2024-03-31)

---

## 7️⃣ 작성 체크리스트

모든 답변은 반드시 다음을 포함해야 합니다:

- [ ] 📌 이모지를 사용한 섹션 구분
- [ ] 계층 구조 (#, ##, ###)
- [ ] 표 (데이터가 있는 경우)
- [ ] 그래프 (추이/비교가 있는 경우)
- [ ] 💡 인사이트 섹션
- [ ] 📎 출처 섹션
- [ ] **굵은 글씨**로 핵심 강조
- [ ] 구분선 (---) 사용

이 형식을 따라 사용자가 바로 보고서로 사용할 수 있는 고품질 답변을 제공하세요!
"""

        # 메모리 컨텍스트 포함 여부에 따라 프롬프트 구성
        if memory_context:
            prompt = f"""
{system_prompt}

{memory_context}

질문: {query}

참고 자료:
{context}

위의 사용자 정보와 이전 대화 내용, 그리고 참고 자료를 바탕으로 질문에 답변하세요.
사용자와의 이전 대화 맥락을 고려하여 자연스럽게 답변하세요.

답변 형식:
1. 답변 내용
2. 표/그래프 (필요 시)
3. 출처 목록

답변:
"""
        else:
            prompt = f"""
{system_prompt}

질문: {query}

참고 자료:
{context}

위 자료를 바탕으로 질문에 답변하세요.
답변 형식:
1. 답변 내용
2. 표/그래프 (필요 시)
3. 출처 목록

답변:
"""

        # LLM 호출
        response = llm.invoke(prompt)
        content = response.content

        # 출처 수집
        sources = ResponseGenerationNode._collect_sources(retrieved_documents)

        # 표/그래프 데이터 추출
        table_data, chart_data = ResponseGenerationNode._extract_structured_data(content)

        # 응답 데이터 생성
        response_data = ResponseData(
            content=content,
            sources=sources,
            confidence_score=ResponseGenerationNode._calculate_confidence(retrieved_documents),
            table_data=table_data,
            chart_data=chart_data
        )

        # 상태 업데이트
        state["response"] = response_data
        state["progress"] = state.get("progress", []) + [{
            "stage": "response_generation",
            "status": "completed",
            "message": "답변 생성 완료"
        }]

        return state

    @staticmethod
    def _build_context(documents: List[RetrievedDocument]) -> str:
        """검색 결과를 컨텍스트로 구성"""
        if not documents:
            return "관련 정보를 찾을 수 없습니다."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            source_type = "부품 정보" if doc.source == "mongodb" else "문서"
            context_parts.append(f"""
[{i}] {source_type}
{doc.content}
출처: {doc.metadata.get('file_name') or doc.metadata.get('part_number', '시스템')}
""")

        return "\n".join(context_parts)

    @staticmethod
    def _collect_sources(documents: List[RetrievedDocument]) -> List[Dict[str, Any]]:
        """출처 정보 수집"""
        sources = []
        for doc in documents:
            source_info = {
                "type": doc.source,
                "metadata": doc.metadata
            }
            if doc.similarity_score:
                source_info["similarity_score"] = doc.similarity_score
            sources.append(source_info)
        return sources

    @staticmethod
    def _extract_structured_data(content: str) -> tuple:
        """응답에서 표/그래프 데이터 추출"""
        table_data = None
        chart_data = None

        # 마크다운 표 감지 (간단한 예시)
        if "|" in content and "---" in content:
            # 실제로는 파싱 필요
            table_data = []

        # JSON 그래프 데이터 감지
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                chart_data = json.loads(json_str)
            except:
                pass

        return table_data, chart_data

    @staticmethod
    def _calculate_confidence(documents: List[RetrievedDocument]) -> float:
        """신뢰도 점수 계산"""
        if not documents:
            return 0.0

        # 간단한 신뢰도 계산
        # - 문서 개수
        # - 유사도 점수
        # - MongoDB 결과 포함 여부
        score = 0.0

        # 문서 개수 (최대 0.3)
        doc_count_score = min(len(documents) / 5, 1.0) * 0.3

        # 평균 유사도 (최대 0.4)
        scores_with_similarity = [d.similarity_score for d in documents if d.similarity_score]
        avg_similarity = sum(scores_with_similarity) / len(scores_with_similarity) if scores_with_similarity else 0.5
        similarity_score = avg_similarity * 0.4

        # MongoDB 포함 여부 (0.3)
        has_mongodb = any(d.source == "mongodb" for d in documents)
        mongodb_score = 0.3 if has_mongodb else 0.0

        score = doc_count_score + similarity_score + mongodb_score

        return round(score, 2)


class QualityCheckNode:
    """
    Node 4: 품질 검증
    - Hallucination 검출
    - 신뢰도 검증
    - 경고 메시지 생성
    """

    @staticmethod
    def execute(state: GraphState) -> GraphState:
        """품질 검증 실행"""
        response_data = state.get("response")
        if not response_data:
            return state

        warnings = []

        # 1. 출처 확인
        if not response_data.sources:
            warnings.append("출처가 없는 답변입니다. 신뢰도가 낮을 수 있습니다.")

        # 2. 신뢰도 확인
        if response_data.confidence_score < 0.5:
            warnings.append("신뢰도가 낮습니다. 답변을 참고용으로만 사용하세요.")

        # 3. 내용 길이 확인
        if len(response_data.content) < 50:
            warnings.append("답변이 너무 짧습니다. 정보가 부족할 수 있습니다.")

        # 경고 추가
        response_data.warnings = warnings

        # 상태 업데이트
        state["response"] = response_data
        state["progress"] = state.get("progress", []) + [{
            "stage": "quality_check",
            "status": "completed",
            "message": "품질 검증 완료"
        }]

        return state
