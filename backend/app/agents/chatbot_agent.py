"""
LangGraph 챗봇 Agent
워크플로우 조립 및 실행
"""
from typing import Dict, Any, Iterator
from langgraph.graph import StateGraph, END
from app.agents.graph_state import GraphState
from app.agents.nodes import (
    QueryAnalysisNode,
    DataRetrievalNode,
    ResponseGenerationNode,
    QualityCheckNode
)
from app.services.memory_service import get_memory_manager, cleanup_memory_cache


class ChatbotAgent:
    """반도체 부품 챗봇 Agent"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """LangGraph 워크플로우 구성"""

        # StateGraph 생성
        workflow = StateGraph(GraphState)

        # 노드 추가
        workflow.add_node("query_analysis", QueryAnalysisNode.execute)
        workflow.add_node("data_retrieval", DataRetrievalNode.execute)
        workflow.add_node("response_generation", ResponseGenerationNode.execute)
        workflow.add_node("quality_check", QualityCheckNode.execute)

        # 엣지 설정
        workflow.set_entry_point("query_analysis")

        # 조건부 라우팅
        workflow.add_conditional_edges(
            "query_analysis",
            self._route_after_analysis,
            {
                "retrieve": "data_retrieval",
                "direct": "response_generation"
            }
        )

        workflow.add_edge("data_retrieval", "response_generation")
        workflow.add_edge("response_generation", "quality_check")
        workflow.add_edge("quality_check", END)

        return workflow.compile()

    def _route_after_analysis(self, state: GraphState) -> str:
        """
        쿼리 분석 후 라우팅 결정
        - 데이터가 필요하면 retrieval
        - 간단한 질문은 바로 응답 생성
        """
        classification = state.get("classification")

        if not classification:
            return "direct"

        # 데이터 소스가 필요한 경우
        if classification.data_sources and classification.data_sources != ["none"]:
            return "retrieve"

        # info_lookup은 바로 응답
        if classification.intent == "info_lookup":
            return "direct"

        return "retrieve"

    def invoke(
        self,
        query: str,
        user_id: str = None,
        conversation_id: str = None,
        custom_prompt: str = None,
        llm_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        챗봇 실행 (동기)

        Args:
            query: 사용자 질문
            user_id: 사용자 ID
            conversation_id: 대화 ID
            custom_prompt: 커스텀 시스템 프롬프트
            llm_config: LLM 설정 (model, temperature)

        Returns:
            응답 데이터
        """
        # 메모리 매니저 가져오기
        memory_manager = None
        if user_id and conversation_id:
            memory_manager = get_memory_manager(user_id, conversation_id)

            # 사용자 메시지 메모리에 추가
            memory_manager.add_message("user", query)

        # 메모리 컨텍스트 생성
        memory_context = memory_manager.get_full_context() if memory_manager else None

        # 초기 상태
        initial_state: GraphState = {
            "query": query,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "custom_prompt": custom_prompt,
            "llm_config": llm_config or {},
            "memory_context": memory_context,
            "classification": None,
            "retrieved_documents": [],
            "mongodb_results": [],
            "vectordb_results": [],
            "response": None,
            "progress": [],
            "error": None
        }

        try:
            # 워크플로우 실행
            final_state = self.graph.invoke(initial_state)

            # 결과 추출
            response_data = final_state.get("response")

            if response_data:
                # Assistant 응답 메모리에 추가
                if memory_manager:
                    memory_manager.add_message(
                        "assistant",
                        response_data.content,
                        metadata={
                            "sources": response_data.sources,
                            "confidence_score": response_data.confidence_score
                        }
                    )

                    # 주기적으로 중요 정보 저장 (메시지가 10개 이상일 때)
                    messages = memory_manager.conversation_memory.get_messages()
                    if len(messages) >= 10:
                        saved_count = memory_manager.save_conversation_memories()
                        if saved_count > 0:
                            print(f"✓ {saved_count}개의 중요 정보를 장기 메모리에 저장했습니다")

                return {
                    "success": True,
                    "content": response_data.content,
                    "sources": response_data.sources,
                    "confidence_score": response_data.confidence_score,
                    "table_data": response_data.table_data,
                    "chart_data": response_data.chart_data,
                    "warnings": response_data.warnings,
                    "progress": final_state.get("progress", [])
                }
            else:
                return {
                    "success": False,
                    "error": "응답 생성 실패",
                    "progress": final_state.get("progress", [])
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "progress": []
            }

    def stream(
        self,
        query: str,
        user_id: str = None,
        conversation_id: str = None,
        custom_prompt: str = None,
        llm_config: Dict[str, Any] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        챗봇 실행 (스트리밍)
        진행 상황을 실시간으로 반환

        Yields:
            진행 상황 업데이트
        """
        # 초기 상태
        initial_state: GraphState = {
            "query": query,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "custom_prompt": custom_prompt,
            "llm_config": llm_config or {},
            "classification": None,
            "retrieved_documents": [],
            "mongodb_results": [],
            "vectordb_results": [],
            "response": None,
            "progress": [],
            "error": None
        }

        try:
            # 워크플로우 스트리밍 실행
            for event in self.graph.stream(initial_state):
                # 이벤트에서 진행 상황 추출
                for node_name, node_state in event.items():
                    progress = node_state.get("progress", [])
                    if progress:
                        latest_progress = progress[-1]
                        yield {
                            "type": "progress",
                            "node": node_name,
                            "data": latest_progress
                        }

                    # 최종 응답
                    if node_name == "quality_check":
                        response_data = node_state.get("response")
                        if response_data:
                            yield {
                                "type": "final",
                                "data": {
                                    "success": True,
                                    "content": response_data.content,
                                    "sources": response_data.sources,
                                    "confidence_score": response_data.confidence_score,
                                    "table_data": response_data.table_data,
                                    "chart_data": response_data.chart_data,
                                    "warnings": response_data.warnings
                                }
                            }

        except Exception as e:
            yield {
                "type": "error",
                "data": {
                    "success": False,
                    "error": str(e)
                }
            }


# 전역 Agent 인스턴스
_agent = None


def get_chatbot_agent() -> ChatbotAgent:
    """챗봇 Agent 인스턴스 반환 (싱글톤)"""
    global _agent
    if _agent is None:
        _agent = ChatbotAgent()
    return _agent
