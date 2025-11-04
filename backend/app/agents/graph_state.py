"""
LangGraph State Definition
"""
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """State for the agent graph"""
    # Messages
    messages: List[Dict[str, str]]

    # Query analysis
    query: str
    query_intent: Optional[str]  # 'material_info', 'document_search', 'general', 'mixed'
    needs_material_data: bool
    needs_document_search: bool
    extracted_material_ids: List[str]

    # Retrieved data
    material_data: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]

    # Memory and context
    conversation_history: List[Dict[str, str]]
    user_preferences: Optional[Dict[str, Any]]
    custom_prompts: List[str]

    # Response generation
    final_response: Optional[str]
    sources: List[Dict[str, Any]]

    # Progress tracking for UI
    current_step: str
    progress: List[Dict[str, str]]  # [{step: 'analyzing', status: 'completed', message: '...'}]

    # Error handling
    error: Optional[str]


class ProgressStep:
    """Progress step constants"""
    ANALYZING = "analyzing"
    RETRIEVING_MATERIALS = "retrieving_materials"
    SEARCHING_DOCUMENTS = "searching_documents"
    GENERATING_RESPONSE = "generating_response"
    COMPLETED = "completed"
    ERROR = "error"


class ProgressStatus:
    """Progress status constants"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
