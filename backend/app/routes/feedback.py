"""
Feedback API routes
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from app.services.database_service import db_service
from app.services.llm_service import llm_service
from app.models.database import Feedback, KnowledgeEntry, Message

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')


@feedback_bp.route('/', methods=['POST'])
def submit_feedback():
    """Submit feedback for a message"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        message_id = data.get('message_id')
        rating = data.get('rating')  # 1-5 or thumbs up/down (1/5)
        comment = data.get('comment')
        improved_response = data.get('improved_response')

        with db_service.get_db() as db:
            # Get the original message for context
            message = None
            query_embedding = None
            if message_id:
                message = db.query(Message).filter(Message.id == message_id).first()
                if message:
                    # Get embedding of the query for similarity search
                    # Find the user message before this assistant message
                    user_msg = db.query(Message).filter(
                        Message.conversation_id == message.conversation_id,
                        Message.id < message_id,
                        Message.role == 'user'
                    ).order_by(Message.id.desc()).first()

                    if user_msg:
                        embedding = llm_service.get_embedding(user_msg.content)
                        query_embedding = embedding

            # Create feedback
            feedback = Feedback(
                user_id=user_id,
                message_id=message_id,
                rating=rating,
                comment=comment,
                query_embedding=query_embedding,
                improved_response=improved_response
            )
            db.add(feedback)
            db.commit()
            db.refresh(feedback)

            # If feedback is positive and has improved response, add to knowledge base
            if rating and rating >= 4 and improved_response:
                _add_to_knowledge_base(db, message, improved_response)

            return jsonify({
                "id": feedback.id,
                "message": "Feedback submitted successfully"
            }), 201

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def _add_to_knowledge_base(db, message, improved_response):
    """Add positive feedback to knowledge base"""
    try:
        if not message:
            return

        # Get the user query
        user_msg = db.query(Message).filter(
            Message.conversation_id == message.conversation_id,
            Message.id < message.id,
            Message.role == 'user'
        ).order_by(Message.id.desc()).first()

        if user_msg:
            # Check if similar entry exists
            existing = db.query(KnowledgeEntry).filter(
                KnowledgeEntry.query_pattern == user_msg.content
            ).first()

            if existing:
                # Update existing entry
                existing.answer = improved_response
                existing.confidence_score += 1
                existing.usage_count += 1
                existing.updated_at = datetime.utcnow()
            else:
                # Create new entry
                entry = KnowledgeEntry(
                    query_pattern=user_msg.content,
                    answer=improved_response,
                    entry_metadata=message.message_metadata or {},
                    confidence_score=1,
                    usage_count=1
                )
                db.add(entry)

            db.commit()
            logger.info(f"Added/updated knowledge entry for query: {user_msg.content[:50]}")

    except Exception as e:
        logger.error(f"Error adding to knowledge base: {e}", exc_info=True)


@feedback_bp.route('/stats', methods=['GET'])
def get_feedback_stats():
    """Get feedback statistics"""
    try:
        user_id = request.args.get('user_id', type=int)

        with db_service.get_db() as db:
            query = db.query(Feedback)
            if user_id:
                query = query.filter(Feedback.user_id == user_id)

            feedbacks = query.all()

            # Calculate stats
            total = len(feedbacks)
            positive = sum(1 for f in feedbacks if f.rating and f.rating >= 4)
            negative = sum(1 for f in feedbacks if f.rating and f.rating <= 2)
            avg_rating = sum(f.rating for f in feedbacks if f.rating) / total if total > 0 else 0

            return jsonify({
                "total_feedback": total,
                "positive": positive,
                "negative": negative,
                "average_rating": round(avg_rating, 2)
            })

    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@feedback_bp.route('/knowledge', methods=['GET'])
def get_knowledge_entries():
    """Get learned knowledge entries"""
    try:
        limit = request.args.get('limit', 50, type=int)

        with db_service.get_db() as db:
            entries = db.query(KnowledgeEntry).order_by(
                KnowledgeEntry.confidence_score.desc()
            ).limit(limit).all()

            return jsonify({
                "entries": [
                    {
                        "id": entry.id,
                        "query_pattern": entry.query_pattern,
                        "answer": entry.answer,
                        "confidence_score": entry.confidence_score,
                        "usage_count": entry.usage_count,
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in entries
                ]
            })

    except Exception as e:
        logger.error(f"Error getting knowledge entries: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
