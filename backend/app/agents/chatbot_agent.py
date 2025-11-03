"""
Main Chatbot Agent using LangGraph
"""
from typing import Dict, Any, Iterator
import logging

from langgraph.graph import StateGraph, END
from app.agents.graph_state import AgentState, ProgressStep
from app.agents.nodes import (
    analyze_query_node,
    retrieve_material_data_node,
    search_documents_node,
    generate_response_node
)

logger = logging.getLogger(__name__)


class ChatbotAgent:
    """Main chatbot agent orchestrating the workflow"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        # Create graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_query", analyze_query_node)
        workflow.add_node("retrieve_materials", retrieve_material_data_node)
        workflow.add_node("search_documents", search_documents_node)
        workflow.add_node("generate_response", generate_response_node)

        # Define edges
        workflow.set_entry_point("analyze_query")

        # After analysis, decide which data sources to query
        workflow.add_edge("analyze_query", "retrieve_materials")
        workflow.add_edge("retrieve_materials", "search_documents")
        workflow.add_edge("search_documents", "generate_response")

        # End after response generation
        workflow.add_edge("generate_response", END)

        # Compile graph
        return workflow.compile()

    def process_query(
        self,
        query: str,
        conversation_history: list = None,
        user_preferences: Dict[str, Any] = None,
        custom_prompts: list = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent graph

        Args:
            query: User query string
            conversation_history: Previous messages in conversation
            user_preferences: User preferences and settings
            custom_prompts: Custom prompts from user

        Returns:
            Dict containing final response, sources, and progress
        """
        logger.info(f"Processing query: {query[:100]}...")

        # Initialize state
        initial_state = {
            "messages": [],
            "query": query,
            "query_intent": None,
            "needs_material_data": False,
            "needs_document_search": False,
            "extracted_material_ids": [],
            "material_data": [],
            "documents": [],
            "conversation_history": conversation_history or [],
            "user_preferences": user_preferences,
            "custom_prompts": custom_prompts or [],
            "final_response": None,
            "sources": [],
            "current_step": "",
            "progress": [],
            "error": None
        }

        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)

            return {
                "response": final_state.get("final_response", ""),
                "sources": final_state.get("sources", []),
                "progress": final_state.get("progress", []),
                "material_data": final_state.get("material_data", []),
                "documents": final_state.get("documents", []),
                "query_intent": final_state.get("query_intent", "general"),
                "error": final_state.get("error")
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "response": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
                "sources": [],
                "progress": [{
                    "step": ProgressStep.ERROR,
                    "status": "error",
                    "message": str(e)
                }],
                "material_data": [],
                "documents": [],
                "query_intent": "error",
                "error": str(e)
            }

    def process_query_stream(
        self,
        query: str,
        conversation_history: list = None,
        user_preferences: Dict[str, Any] = None,
        custom_prompts: list = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Process query with streaming updates for progress

        Yields progress updates and final response
        """
        logger.info(f"Processing query (streaming): {query[:100]}...")

        # Initialize state
        initial_state = {
            "messages": [],
            "query": query,
            "query_intent": None,
            "needs_material_data": False,
            "needs_document_search": False,
            "extracted_material_ids": [],
            "material_data": [],
            "documents": [],
            "conversation_history": conversation_history or [],
            "user_preferences": user_preferences,
            "custom_prompts": custom_prompts or [],
            "final_response": None,
            "sources": [],
            "current_step": "",
            "progress": [],
            "error": None
        }

        try:
            # Stream the graph execution
            for event in self.graph.stream(initial_state):
                # Each event is a dict with node name as key
                for node_name, node_state in event.items():
                    # Send progress update
                    if node_state.get("progress"):
                        latest_progress = node_state["progress"][-1]
                        yield {
                            "type": "progress",
                            "step": latest_progress["step"],
                            "status": latest_progress["status"],
                            "message": latest_progress["message"]
                        }

            # After all nodes complete, send final response
            # Re-run to get final state (since stream gives incremental updates)
            final_state = self.graph.invoke(initial_state)

            yield {
                "type": "response",
                "response": final_state.get("final_response", ""),
                "sources": final_state.get("sources", []),
                "material_data": final_state.get("material_data", []),
                "documents": final_state.get("documents", []),
                "query_intent": final_state.get("query_intent", "general")
            }

        except Exception as e:
            logger.error(f"Error in streaming query: {e}", exc_info=True)
            yield {
                "type": "error",
                "message": str(e)
            }


# Global agent instance
chatbot_agent = ChatbotAgent()
