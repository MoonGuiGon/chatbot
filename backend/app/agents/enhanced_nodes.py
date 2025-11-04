"""
Enhanced LangGraph Agent Nodes with Multimodal RAG and Knowledge Graph
"""
import re
import json
from typing import Dict, Any, List
import logging
import base64
from pathlib import Path

from app.agents.graph_state import AgentState, ProgressStep, ProgressStatus
from app.services.llm_service import llm_service
from app.services.database_service import mongodb_service
from app.services.pgvector_service import pgvector_service
from app.services.vision_service import vision_service
from app.services.ontology_service import ontology_service
from app.services.cache_service import cache_service, cache_result

logger = logging.getLogger(__name__)


def analyze_query_node_enhanced(state: AgentState) -> AgentState:
    """
    Enhanced query analysis with caching and ontology check
    """
    logger.info("Node: Enhanced Query Analysis")

    query = state["query"]

    # Update progress
    state["current_step"] = ProgressStep.ANALYZING
    state["progress"].append({
        "step": ProgressStep.ANALYZING,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "질문을 분석하고 있습니다..."
    })

    # Check cache first for similar queries
    cached_result = cache_service.get_cached_query_result(query)
    if cached_result:
        logger.info("Cache hit for query analysis")
        state["progress"][-1]["status"] = ProgressStatus.COMPLETED
        state["progress"][-1]["message"] = "질문 분석 완료 (캐시에서 복원)"
        return cached_result

    # Extract material IDs
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

    # Use ontology to find related entities
    related_entities = []
    if material_ids:
        for mat_id in material_ids:
            entities = ontology_service.find_related_entities(
                'Material', 'materialId', mat_id, max_depth=1
            )
            related_entities.extend(entities)

    # LLM-based intent classification
    intent_messages = [
        {
            "role": "system",
            "content": """질문 의도를 분석하여 JSON으로 응답하세요:
{
  "intent": "material_info | document_search | general | mixed",
  "reason": "이유",
  "requires_visual": true/false,  # 차트/표/이미지 분석 필요 여부
  "complexity": "simple | moderate | complex"
}"""
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
            try:
                intent_data = json.loads(content)
                intent = intent_data.get('intent', 'general')
                requires_visual = intent_data.get('requires_visual', False)
            except:
                intent = 'mixed' if (needs_material and needs_docs) else ('material_info' if needs_material else ('document_search' if needs_docs else 'general'))
                requires_visual = False
        else:
            intent = 'general'
            requires_visual = False
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        intent = 'general'
        requires_visual = False

    # Update state
    state["query_intent"] = intent
    state["needs_material_data"] = intent in ['material_info', 'mixed'] or needs_material
    state["needs_document_search"] = intent in ['document_search', 'mixed'] or needs_docs or requires_visual
    state["extracted_material_ids"] = material_ids
    state["related_entities"] = related_entities
    state["requires_visual_analysis"] = requires_visual

    # Complete analysis step
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = f"질문 분석 완료 (의도: {intent}, 시각 분석: {'필요' if requires_visual else '불필요'})"

    logger.info(f"Enhanced query analysis: intent={intent}, visual={requires_visual}, entities={len(related_entities)}")

    return state


def retrieve_material_data_node_enhanced(state: AgentState) -> AgentState:
    """
    Enhanced material retrieval with knowledge graph context
    """
    if not state.get("needs_material_data", False):
        return state

    logger.info("Node: Enhanced Material Retrieval")

    state["current_step"] = ProgressStep.RETRIEVING_MATERIALS
    state["progress"].append({
        "step": ProgressStep.RETRIEVING_MATERIALS,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "MongoDB 및 지식 그래프에서 부품 정보를 조회하고 있습니다..."
    })

    material_data = []
    material_ids = state.get("extracted_material_ids", [])

    # Retrieve materials with knowledge graph context
    for material_id in material_ids:
        # Get base material data
        material = mongodb_service.get_material(material_id)
        if material:
            # Enrich with knowledge graph context
            kg_context = ontology_service.get_material_context(material_id)

            material['kg_context'] = {
                'suppliers': kg_context.get('suppliers', []),
                'equipment': kg_context.get('equipment', []),
                'related_documents': kg_context.get('documents', []),
                'similar_materials': kg_context.get('similar_materials', [])
            }

            material_data.append(material)

    # If no specific IDs, search based on query
    if not material_data:
        materials = mongodb_service.search_materials({}, limit=3)
        material_data.extend(materials)

    state["material_data"] = material_data

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = f"부품 정보 {len(material_data)}개 조회 완료 (지식 그래프 컨텍스트 포함)"

    logger.info(f"Retrieved {len(material_data)} materials with KG context")

    return state


def search_documents_multimodal_node(state: AgentState) -> AgentState:
    """
    Enhanced document search with vision model integration
    Retrieves both text and associated screenshots
    """
    if not state.get("needs_document_search", False):
        return state

    logger.info("Node: Multimodal Document Search")

    state["current_step"] = ProgressStep.SEARCHING_DOCUMENTS
    state["progress"].append({
        "step": ProgressStep.SEARCHING_DOCUMENTS,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "pgvector에서 관련 문서 및 스크린샷을 검색하고 있습니다..."
    })

    query = state["query"]
    requires_visual = state.get("requires_visual_analysis", False)

    # Generate query embedding
    query_embedding = llm_service.get_embedding(query)

    if not query_embedding:
        state["documents"] = []
        state["progress"][-1]["status"] = ProgressStatus.COMPLETED
        state["progress"][-1]["message"] = "문서 검색 건너뜀"
        return state

    # Search in pgvector
    documents = pgvector_service.search_similar(
        query_embedding=query_embedding,
        n_results=5
    )

    # If visual analysis is required, analyze screenshots
    if requires_visual and documents:
        for doc in documents:
            screenshot_path = doc.get('screenshot_path')
            if screenshot_path and Path(screenshot_path).exists():
                # Analyze screenshot with vision model
                vision_analysis = vision_service.analyze_document_image(
                    screenshot_path,
                    prompt=f"이 문서 이미지를 분석하여 '{query}'와 관련된 정보를 추출하세요."
                )
                doc['vision_analysis'] = vision_analysis

    state["documents"] = documents

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    msg = f"관련 문서 {len(documents)}개 검색 완료"
    if requires_visual:
        visual_count = sum(1 for d in documents if d.get('vision_analysis'))
        msg += f" (시각 분석: {visual_count}개)"
    state["progress"][-1]["message"] = msg

    logger.info(f"Found {len(documents)} documents, visual analysis: {requires_visual}")

    return state


def generate_response_node_enhanced(state: AgentState) -> AgentState:
    """
    Enhanced response generation with multimodal context and knowledge graph
    """
    logger.info("Node: Enhanced Response Generation")

    state["current_step"] = ProgressStep.GENERATING_RESPONSE
    state["progress"].append({
        "step": ProgressStep.GENERATING_RESPONSE,
        "status": ProgressStatus.IN_PROGRESS,
        "message": "멀티모달 컨텍스트로 답변을 생성하고 있습니다..."
    })

    # Build comprehensive context
    context_parts = []
    sources = []

    # 1. Material data with KG context
    if state.get("material_data"):
        context_parts.append("## 부품 정보 (MongoDB + 지식 그래프)\n")
        for material in state["material_data"]:
            context_parts.append(f"**자재코드**: {material.get('materialId', 'N/A')}")
            context_parts.append(f"**부품명**: {material.get('name', 'N/A')}")

            # Add KG context
            kg_ctx = material.get('kg_context', {})
            if kg_ctx.get('suppliers'):
                suppliers = [s.get('name', 'N/A') for s in kg_ctx['suppliers']]
                context_parts.append(f"**공급업체**: {', '.join(suppliers)}")
            if kg_ctx.get('similar_materials'):
                similar = [m.get('materialId', 'N/A') for m in kg_ctx['similar_materials'][:3]]
                context_parts.append(f"**유사 부품**: {', '.join(similar)}")

            context_parts.append("")

            sources.append({
                "type": "mongodb",
                "material_id": material.get('materialId', 'N/A'),
                "data": material
            })

    # 2. Document data with vision analysis
    if state.get("documents"):
        context_parts.append("\n## 관련 문서 (pgvector + Vision Model)\n")
        for i, doc in enumerate(state["documents"], 1):
            source_name = doc['metadata'].get('source', 'Unknown')
            context_parts.append(f"### 문서 {i}: {source_name}")

            # Text content
            context_parts.append(doc['content'][:400] + "...")

            # Vision analysis if available
            if doc.get('vision_analysis'):
                va = doc['vision_analysis']
                context_parts.append(f"\n**시각 분석 요약**: {va.get('summary', 'N/A')}")
                if va.get('key_points'):
                    context_parts.append("**핵심 포인트**:")
                    for point in va['key_points'][:3]:
                        context_parts.append(f"- {point}")

            context_parts.append("")

            sources.append({
                "type": "document",
                "source": source_name,
                "metadata": doc['metadata'],
                "has_visual_analysis": bool(doc.get('vision_analysis'))
            })

    context = "\n".join(context_parts)

    # Build messages for LLM
    system_prompt = f"""당신은 반도체 장비 부품 관리 전문 AI 어시스턴트입니다.

**역할:**
- 사용자의 질문에 정확하고 구체적으로 답변합니다
- 제공된 부품 정보, 문서, 시각 분석을 종합적으로 활용합니다
- 지식 그래프의 관계 정보를 활용하여 연관 정보를 제공합니다
- 추측하지 않고 확실한 정보만 제공합니다
- 정보의 출처를 명확히 밝힙니다

**답변 형식:**
1. 질문에 대한 직접적인 답변
2. 관련 데이터 (표 형식 활용)
3. 시각 자료 분석 결과 (있는 경우)
4. 연관 정보 및 권장 사항
5. 출처 표시

**주의사항:**
- 환각(hallucination) 방지: 제공된 컨텍스트에 없는 정보는 만들지 마세요
- 불확실한 경우 솔직히 "정보가 부족합니다"라고 말하세요
"""

    # Add custom prompts
    if state.get("custom_prompts"):
        system_prompt += "\n\n## 사용자 맞춤 지침:\n" + "\n".join(f"- {p}" for p in state["custom_prompts"])

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    history = state.get("conversation_history", [])[-5:]
    messages.extend(history)

    # Add current query with context
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

    # Cache the result
    cache_service.cache_query_result(state["query"], {
        "response": final_response,
        "sources": sources,
        "intent": state.get("query_intent")
    }, ttl=1800)  # 30 minutes

    # Update progress
    state["progress"][-1]["status"] = ProgressStatus.COMPLETED
    state["progress"][-1]["message"] = "답변 생성 완료 (멀티모달 컨텍스트 활용)"

    state["current_step"] = ProgressStep.COMPLETED
    state["progress"].append({
        "step": ProgressStep.COMPLETED,
        "status": ProgressStatus.COMPLETED,
        "message": "모든 작업 완료"
    })

    return state
