"""
Chat API routes
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import logging
from datetime import datetime

from app.agents.chatbot_agent import chatbot_agent
from app.services.database_service import db_service
from app.models.database import User, Conversation, Message, UserSettings

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('/query', methods=['POST'])
def query():
    """
    Process a chat query (non-streaming)
    """
    try:
        data = request.json
        query_text = data.get('query', '')
        user_id = data.get('user_id', 1)  # Default user for testing
        conversation_id = data.get('conversation_id')

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        # Get user settings
        with db_service.get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                # Create default user
                user = User(username=f"user_{user_id}", email=f"user_{user_id}@example.com")
                db.add(user)
                db.commit()
                db.refresh(user)

            settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            custom_prompts = settings.custom_prompts if settings and settings.custom_prompts else []

            # Get or create conversation
            if conversation_id:
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            else:
                conversation = Conversation(
                    user_id=user_id,
                    title=query_text[:50] + "..." if len(query_text) > 50 else query_text
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                conversation_id = conversation.id

            # Get conversation history
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(10).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]

        # Process query
        result = chatbot_agent.process_query(
            query=query_text,
            conversation_history=conversation_history,
            custom_prompts=custom_prompts
        )

        # Save messages to database
        with db_service.get_db() as db:
            # User message
            user_msg = Message(
                conversation_id=conversation_id,
                role="user",
                content=query_text,
                metadata={}
            )
            db.add(user_msg)

            # Assistant message
            assistant_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=result['response'],
                metadata={
                    "sources": result['sources'],
                    "query_intent": result['query_intent'],
                    "material_data": result['material_data'],
                    "documents": [{"source": d['metadata'].get('source')} for d in result['documents']]
                }
            )
            db.add(assistant_msg)
            db.commit()

        return jsonify({
            "conversation_id": conversation_id,
            "response": result['response'],
            "sources": result['sources'],
            "progress": result['progress'],
            "query_intent": result['query_intent']
        })

    except Exception as e:
        logger.error(f"Error in query endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/query/stream', methods=['POST'])
def query_stream():
    """
    Process a chat query with streaming response
    """
    try:
        data = request.json
        query_text = data.get('query', '')
        user_id = data.get('user_id', 1)
        conversation_id = data.get('conversation_id')

        if not query_text:
            return jsonify({"error": "Query is required"}), 400

        # Get user settings and conversation history
        with db_service.get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(username=f"user_{user_id}", email=f"user_{user_id}@example.com")
                db.add(user)
                db.commit()
                db.refresh(user)

            settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            custom_prompts = settings.custom_prompts if settings and settings.custom_prompts else []

            if conversation_id:
                conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            else:
                conversation = Conversation(
                    user_id=user_id,
                    title=query_text[:50] + "..." if len(query_text) > 50 else query_text
                )
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                conversation_id = conversation.id

            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(10).all()
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]

        def generate():
            """Generator for streaming response"""
            response_data = None

            for event in chatbot_agent.process_query_stream(
                query=query_text,
                conversation_history=conversation_history,
                custom_prompts=custom_prompts
            ):
                # Send event as SSE (Server-Sent Events)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                if event.get('type') == 'response':
                    response_data = event

            # Save to database after streaming completes
            if response_data:
                with db_service.get_db() as db:
                    user_msg = Message(
                        conversation_id=conversation_id,
                        role="user",
                        content=query_text,
                        metadata={}
                    )
                    db.add(user_msg)

                    assistant_msg = Message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_data['response'],
                        metadata={
                            "sources": response_data['sources'],
                            "query_intent": response_data['query_intent']
                        }
                    )
                    db.add(assistant_msg)
                    db.commit()

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        logger.error(f"Error in stream endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
