"""
Conversation management API routes
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from app.services.database_service import db_service
from app.models.database import User, Conversation, Message

logger = logging.getLogger(__name__)

conversation_bp = Blueprint('conversation', __name__, url_prefix='/api/conversations')


@conversation_bp.route('/', methods=['GET'])
def get_conversations():
    """Get all conversations for a user"""
    try:
        user_id = request.args.get('user_id', 1, type=int)

        with db_service.get_db() as db:
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_archived == False
            ).order_by(Conversation.updated_at.desc()).all()

            return jsonify({
                "conversations": [
                    {
                        "id": conv.id,
                        "title": conv.title,
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat()
                    }
                    for conv in conversations
                ]
            })

    except Exception as e:
        logger.error(f"Error getting conversations: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with messages"""
    try:
        with db_service.get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()

            return jsonify({
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "metadata": msg.message_metadata,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            })

    except Exception as e:
        logger.error(f"Error getting conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        title = data.get('title', 'New Conversation')

        with db_service.get_db() as db:
            conversation = Conversation(
                user_id=user_id,
                title=title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            return jsonify({
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat()
            }), 201

    except Exception as e:
        logger.error(f"Error creating conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/<int:conversation_id>', methods=['PUT'])
def update_conversation(conversation_id):
    """Update conversation (e.g., title)"""
    try:
        data = request.json
        title = data.get('title')

        with db_service.get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            if title:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()

            db.commit()

            return jsonify({
                "id": conversation.id,
                "title": conversation.title,
                "updated_at": conversation.updated_at.isoformat()
            })

    except Exception as e:
        logger.error(f"Error updating conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@conversation_bp.route('/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete (archive) a conversation"""
    try:
        with db_service.get_db() as db:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            conversation.is_archived = True
            db.commit()

            return jsonify({"message": "Conversation deleted successfully"})

    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
