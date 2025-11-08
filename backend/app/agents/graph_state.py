"""
LangGraph State 정의
워크플로우 전체에서 공유되는 상태
"""
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class QueryClassification:
    """쿼리 분류 결과"""
    intent: str  # info_lookup, part_search, document_search, general
    data_sources: List[str]  # mongodb, vectordb, both, none
    entities: Dict[str, List[str]]  # part_numbers, part_names, date_ranges, metrics
    requires_calculation: bool
    response_format: str  # text, table, chart, mixed


@dataclass
class RetrievedDocument:
    """검색된 문서"""
    content: str
    source: str  # mongodb, vectordb
    metadata: Dict[str, Any]
    similarity_score: Optional[float] = None


@dataclass
class ResponseData:
    """생성된 응답"""
    content: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    table_data: Optional[List[Dict[str, Any]]] = None
    chart_data: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)


class GraphState(TypedDict):
    """
    LangGraph 워크플로우 전체 상태
    각 노드는 이 상태를 읽고 업데이트
    """
    # 입력
    query: str
    user_id: Optional[str]
    conversation_id: Optional[str]
    custom_prompt: Optional[str]
    llm_config: Optional[Dict[str, Any]]  # model, temperature 등

    # Memory Context (메모리 컨텍스트)
    memory_context: Optional[str]  # 단기 + 장기 메모리

    # Query Analysis
    classification: Optional[QueryClassification]

    # Retrieval
    retrieved_documents: List[RetrievedDocument]
    mongodb_results: List[Dict[str, Any]]
    vectordb_results: List[Dict[str, Any]]

    # Response Generation
    response: Optional[ResponseData]

    # Progress Tracking (프론트엔드 진행 상태 표시용)
    progress: List[Dict[str, str]]  # [{"stage": "분석 중", "status": "completed"}]

    # Error Handling
    error: Optional[str]
