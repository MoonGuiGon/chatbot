"""
설정 API 라우트
"""
from flask import Blueprint, request, jsonify
from app.config import config

bp = Blueprint("settings", __name__)


@bp.route("/settings", methods=["GET"])
def get_settings():
    """현재 설정 조회"""
    return jsonify({
        "success": True,
        "settings": {
            "llm": {
                "chat_model": config.llm.chat_model,
                "embedding_model": config.llm.embedding_model,
                "vision_model": config.llm.vision_model,
                "temperature": config.llm.temperature,
                "max_tokens": config.llm.max_tokens
            },
            "rag": {
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "top_k_documents": config.top_k_documents,
                "confidence_threshold": config.confidence_threshold
            },
            "test_mode": config.test_mode
        }
    })


@bp.route("/settings/llm", methods=["POST"])
def update_llm_settings():
    """
    LLM 설정 업데이트 (세션별)

    Request:
        {
            "model": "gpt-4",
            "temperature": 0.2,
            "max_tokens": 3000
        }

    Response:
        {
            "success": true,
            "message": "설정이 업데이트되었습니다."
        }
    """
    data = request.get_json()

    # 임시 설정 업데이트 (세션별 적용)
    # 실제 config는 변경하지 않음
    session_config = {
        "model": data.get("model", config.llm.chat_model),
        "temperature": data.get("temperature", config.llm.temperature),
        "max_tokens": data.get("max_tokens", config.llm.max_tokens)
    }

    return jsonify({
        "success": True,
        "message": "설정이 업데이트되었습니다.",
        "config": session_config
    })


@bp.route("/settings/models", methods=["GET"])
def get_available_models():
    """사용 가능한 모델 목록"""
    return jsonify({
        "success": True,
        "models": {
            "chat": [
                "gpt-4",
                "gpt-3.5-turbo",
                "custom-model-1",
                "custom-model-2"
            ],
            "embedding": [
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large"
            ],
            "vision": [
                "gpt-4-vision",
                "custom-vision-model"
            ]
        }
    })
