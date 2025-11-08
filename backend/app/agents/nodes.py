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
당신은 반도체 부품 전문 챗봇입니다.

중요 규칙:
1. 반드시 제공된 문서와 데이터만 참조하여 답변하세요.
2. 확실하지 않으면 "정보가 부족합니다"라고 답변하세요.
3. 모든 답변에 출처를 명시하세요.
4. 표나 그래프로 표현할 수 있는 내용은 마크다운 표 형식으로 작성하세요.
5. Hallucination을 절대 하지 마세요.
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
