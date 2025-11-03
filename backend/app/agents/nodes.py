"""
LangGraph Agent Nodes
"""
import re
import json
from typing import Dict, Any, List
import logging

from app.agents.graph_state import AgentState, ProgressStep, ProgressStatus
from app.services.llm_service import llm_service
from app.services.database_service import mongodb_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)


def analyze_query_node(state: AgentState) -> AgentState:
    """
    Analyze user query to determine what data sources are needed
    """
    logger.info("Node: Analyzing query")

    query = state["query"]

    # Update progress
    state["current_step"] = ProgressStep.ANALYZING
    state["progress"].append({
        "step": ProgressStep.ANALYZING,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "질문을 분석하고 있습니다..."
    })

    # Extract material IDs (format: MAT-XXX or similar patterns)
    material_id_pattern = r'\b[A-Z]{2,4}-\d{3,6}\b'
    material_ids = re.findall(material_id_pattern, query.upper())

    # Check for material-related keywords
    material_keywords = [
        '부품', '자재', '재고', '구매', '출고', '장착', '장비',
        'materialId', 'material', '코드', '사양', '스펙'
    ]
    needs_material = any(keyword in query.lower() for keyword in material_keywords) or len(material_ids) > 0

    # Check for document search keywords
    doc_keywords = [
        '문서', '지침', '가이드', '매뉴얼', '보고서', '자료',
        '어떻게', '방법', '절차', '기준', '정책'
    ]
    needs_docs = any(keyword in query for keyword in doc_keywords)

    # Determine intent using LLM
    intent_messages = [
        {
            "role": "system",
            "content": """당신은 질문 의도 분석 전문가입니다.
사용자 질문을 분석하여 다음 중 하나로 분류하세요:
- material_info: 부품/자재 정보가 필요한 경우
- document_search: 문서/지침/가이드 검색이 필요한 경우
- general: 일반적인 질문
- mixed: 부품 정보와 문서 검색 모두 필요한 경우

JSON 형식으로 응답하세요: {"intent": "...", "reason": "..."}"""
        },
        {
            "role": "user",
            "content": f"질문: {query}"
        }
    ]

    try:
        response = llm_service.chat_completion(intent_messages, stream=False, temperature=0.3)
        if 'choices' in response:
            content = response['choices'][0]['message']['content']
            # Try to parse JSON
            try:
                intent_data = json.loads(content)
                intent = intent_data.get('intent', 'general')
            except:
                # Fallback to simple detection
                intent = 'mixed' if (needs_material and needs_docs) else ('material_info' if needs_material else ('document_search' if needs_docs else 'general'))
        else:
            intent = 'general'
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        intent = 'mixed' if (needs_material and needs_docs) else ('material_info' if needs_material else ('document_search' if needs_docs else 'general'))

    # Update state
    state["query_intent"] = intent
    state["needs_material_data"] = intent in ['material_info', 'mixed'] or needs_material
    state["needs_document_search"] = intent in ['document_search', 'mixed'] or needs_docs or (not needs_material and intent == 'general')
    state["extracted_material_ids"] = material_ids

    # Complete analysis step
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = f"질문 분석 완료 (의도: {intent})"

    logger.info(f"Query analysis: intent={intent}, needs_material={state['needs_material_data']}, needs_docs={state['needs_document_search']}")

    return state


def retrieve_material_data_node(state: AgentState) -> AgentState:
    """
    Retrieve material data from MongoDB
    """
    if not state.get("needs_material_data", False):
        return state

    logger.info("Node: Retrieving material data")

    state["current_step"] = ProgressStep.RETRIEVING_MATERIALS
    state["progress"].append({
        "step": ProgressStep.RETRIEVING_MATERIALS,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "MongoDB에서 부품 정보를 조회하고 있습니다..."
    })

    material_data = []
    material_ids = state.get("extracted_material_ids", [])

    # Retrieve materials by ID
    for material_id in material_ids:
        material = mongodb_service.get_material(material_id)
        if material:
            material_data.append(material)

    # If no specific IDs, try to search based on query
    if not material_data:
        # Simple keyword-based search
        query = state["query"]
        # In real scenario, you would do more sophisticated search
        # For now, get sample materials
        materials = mongodb_service.search_materials({}, limit=3)
        material_data.extend(materials)

    state["material_data"] = material_data

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = f"부품 정보 {len(material_data)}개 조회 완료"

    logger.info(f"Retrieved {len(material_data)} materials")

    return state


def search_documents_node(state: AgentState) -> AgentState:
    """
    Search relevant documents from VectorDB
    """
    if not state.get("needs_document_search", False):
        return state

    logger.info("Node: Searching documents")

    state["current_step"] = ProgressStep.SEARCHING_DOCUMENTS
    state["progress"].append({
        "step": ProgressStep.SEARCHING_DOCUMENTS,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "VectorDB에서 관련 문서를 검색하고 있습니다..."
    })

    query = state["query"]

    # Search documents
    documents = vector_service.search(query, n_results=5)

    state["documents"] = documents

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = f"관련 문서 {len(documents)}개 검색 완료"

    logger.info(f"Found {len(documents)} relevant documents")

    return state


def generate_response_node(state: AgentState) -> AgentState:
    """
    Generate final response using LLM with retrieved context
    """
    logger.info("Node: Generating response")

    state["current_step"] = ProgressStep.GENERATING_RESPONSE
    state["progress"].append({
        "step": ProgressStep.GENERATING_RESPONSE,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "답변을 생성하고 있습니다..."
    })

    # Build context
    context_parts = []
    sources = []

    # Add material data
    if state.get("material_data"):
        context_parts.append("## 부품 정보 (MongoDB)\n")
        for material in state["material_data"]:
            context_parts.append(f"**자재코드**: {material.get('materialId', 'N/A')}")
            context_parts.append(f"**부품명**: {material.get('name', 'N/A')}")
            context_parts.append(f"**카테고리**: {material.get('category', 'N/A')}")
            if material.get('inventory'):
                inv = material['inventory']
                context_parts.append(f"**재고**: {inv.get('current_stock', 0)}개 (최소: {inv.get('minimum_stock', 0)}개)")
            context_parts.append("")

            sources.append({
                "type": "mongodb",
                "material_id": material.get('materialId', 'N/A'),
                "data": material
            })

    # Add document data
    if state.get("documents"):
        context_parts.append("\n## 관련 문서 (VectorDB)\n")
        for i, doc in enumerate(state["documents"], 1):
            context_parts.append(f"### 문서 {i}: {doc['metadata'].get('source', 'Unknown')}")
            context_parts.append(doc['content'][:500] + "...")
            context_parts.append("")

            sources.append({
                "type": "document",
                "source": doc['metadata'].get('source', 'Unknown'),
                "metadata": doc['metadata']
            })

    context = "\n".join(context_parts)

    # Add conversation history
    history_messages = state.get("conversation_history", [])[-5:]  # Last 5 messages

    # Add custom prompts from user settings
    custom_prompts_text = ""
    if state.get("custom_prompts"):
        custom_prompts_text = "\n\n## 사용자 맞춤 지침:\n" + "\n".join(f"- {p}" for p in state["custom_prompts"])

    # Build messages for LLM
    system_prompt = f"""당신은 반도체 장비 부품 관리 전문 AI 어시스턴트입니다.

**역할:**
- 사용자의 질문에 정확하고 구체적으로 답변합니다
- 제공된 부품 정보와 문서를 바탕으로 답변합니다
- 추측하지 않고 확실한 정보만 제공합니다
- 정보의 출처를 명확히 밝힙니다
- 표와 구조화된 형식으로 정보를 제시합니다

**답변 형식:**
1. 질문에 대한 직접적인 답변
2. 관련 데이터 (표 형식 사용)
3. 상세 설명
4. 권장 사항 (필요한 경우)
5. 출처 표시

**주의사항:**
- 환각(hallucination) 방지: 제공된 컨텍스트에 없는 정보는 만들지 마세요
- 불확실한 경우 솔직히 "정보가 부족합니다"라고 말하세요
- 출처가 명확한 정보만 사용하세요{custom_prompts_text}
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_messages)

    if context:
        messages.append({
            "role": "user",
            "content": f"다음 컨텍스트를 참고하여 답변해주세요:\n\n{context}\n\n질문: {state['query']}"
        })
    else:
        messages.append({
            "role": "user",
            "content": state["query"]
        })

    # Generate response
    try:
        response = llm_service.chat_completion(messages, stream=False, temperature=0.7, max_tokens=2000)

        if 'choices' in response:
            final_response = response['choices'][0]['message']['content']
        else:
            final_response = "죄송합니다. 응답 생성에 실패했습니다."
    except Exception as e:
        logger.error(f"Response generation error: {e}")
        final_response = f"오류가 발생했습니다: {str(e)}"
        state["error"] = str(e)

    state["final_response"] = final_response
    state["sources"] = sources

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = "답변 생성 완료"

    state["current_step"] = ProgressStep.COMPLETED
    state["progress"].append({
        "step": ProgressStep.COMPLETED,
        "status": ProgressStatus.COMPLETED,
        "message": "모든 작업 완료"
    })

    return state
