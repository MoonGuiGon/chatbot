"""
User settings API routes
"""
from flask import Blueprint, request, jsonify
import logging

from app.services.database_service import db_service
from app.models.database import User, UserSettings

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/<int:user_id>', methods=['GET'])
def get_settings(user_id):
    """Get user settings"""
    try:
        with db_service.get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            settings = db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()

            if not settings:
                # Create default settings
                settings = UserSettings(
                    user_id=user_id,
                    custom_prompts=[],
                    preferences={}
                )
                db.add(settings)
                db.commit()
                db.refresh(settings)

            return jsonify({
                "user_id": user_id,
                "custom_prompts": settings.custom_prompts or [],
                "preferences": settings.preferences or {}
            })

    except Exception as e:
        logger.error(f"Error getting settings: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/<int:user_id>', methods=['PUT'])
def update_settings(user_id):
    """Update user settings"""
    try:
        data = request.json
        custom_prompts = data.get('custom_prompts')
        preferences = data.get('preferences')

        with db_service.get_db() as db:
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()

            if not settings:
                # Create new settings
                settings = UserSettings(
                    user_id=user_id,
                    custom_prompts=custom_prompts or [],
                    preferences=preferences or {}
                )
                db.add(settings)
            else:
                # Update existing settings
                if custom_prompts is not None:
                    settings.custom_prompts = custom_prompts
                if preferences is not None:
                    settings.preferences = preferences

            db.commit()
            db.refresh(settings)

            return jsonify({
                "user_id": user_id,
                "custom_prompts": settings.custom_prompts or [],
                "preferences": settings.preferences or {},
                "message": "Settings updated successfully"
            })

    except Exception as e:
        logger.error(f"Error updating settings: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/<int:user_id>/prompts', methods=['POST'])
def add_custom_prompt(user_id):
    """Add a custom prompt"""
    try:
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        with db_service.get_db() as db:
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()

            if not settings:
                settings = UserSettings(
                    user_id=user_id,
                    custom_prompts=[prompt],
                    preferences={}
                )
                db.add(settings)
            else:
                if not settings.custom_prompts:
                    settings.custom_prompts = []
                settings.custom_prompts.append(prompt)

            db.commit()
            db.refresh(settings)

            return jsonify({
                "custom_prompts": settings.custom_prompts,
                "message": "Custom prompt added"
            })

    except Exception as e:
        logger.error(f"Error adding custom prompt: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/<int:user_id>/prompts/<int:index>', methods=['DELETE'])
def delete_custom_prompt(user_id, index):
    """Delete a custom prompt by index"""
    try:
        with db_service.get_db() as db:
            settings = db.query(UserSettings).filter(
                UserSettings.user_id == user_id
            ).first()

            if not settings or not settings.custom_prompts:
                return jsonify({"error": "No custom prompts found"}), 404

            if index < 0 or index >= len(settings.custom_prompts):
                return jsonify({"error": "Invalid index"}), 400

            settings.custom_prompts.pop(index)
            db.commit()

            return jsonify({
                "custom_prompts": settings.custom_prompts,
                "message": "Custom prompt deleted"
            })

    except Exception as e:
        logger.error(f"Error deleting custom prompt: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
