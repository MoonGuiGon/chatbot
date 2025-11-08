"""
메모리 관리 API 라우트
"""
from flask import Blueprint, request, jsonify
from app.services.memory_service import get_memory_manager
from app.services.database_service import get_mongodb

bp = Blueprint("memory", __name__)


@bp.route("/memory/<user_id>", methods=["GET"])
def get_user_memories(user_id):
    """
    사용자 메모리 조회

    Query Parameters:
        - category: 카테고리 필터 (optional)
        - importance: 중요도 필터 (optional)
    """
    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)

    category = request.args.get("category")
    importance = request.args.get("importance")

    memories = user_memory.get_memories(category=category, importance=importance)

    return jsonify({
        "success": True,
        "user_id": user_id,
        "memories": memories,
        "total": len(memories)
    })


@bp.route("/memory/<user_id>/<memory_id>", methods=["DELETE"])
def delete_memory(user_id, memory_id):
    """특정 메모리 삭제"""
    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)
    user_memory.delete_memory(memory_id)

    return jsonify({
        "success": True,
        "message": "메모리가 삭제되었습니다."
    })


@bp.route("/memory/<user_id>/clear", methods=["POST"])
def clear_all_memories(user_id):
    """모든 메모리 초기화"""
    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)
    user_memory.clear_all_memories()

    return jsonify({
        "success": True,
        "message": "모든 메모리가 초기화되었습니다."
    })


@bp.route("/memory/<user_id>/save", methods=["POST"])
def save_conversation_memory(user_id):
    """
    현재 대화에서 중요 정보 추출 및 저장

    Request:
        {
            "conversation_id": "conv-xyz"
        }
    """
    data = request.get_json()
    conversation_id = data.get("conversation_id")

    if not conversation_id:
        return jsonify({
            "success": False,
            "error": "conversation_id가 필요합니다."
        }), 400

    memory_manager = get_memory_manager(user_id, conversation_id)
    saved_count = memory_manager.save_conversation_memories()

    return jsonify({
        "success": True,
        "saved_count": saved_count,
        "message": f"{saved_count}개의 중요 정보를 저장했습니다."
    })


@bp.route("/memory/<user_id>/manual", methods=["POST"])
def add_manual_memory(user_id):
    """
    사용자가 수동으로 메모리 추가

    Request:
        {
            "category": "선호도|역할|자주조회|명시적요청|업무컨텍스트",
            "key": "키워드",
            "value": "내용",
            "importance": "high|medium|low"
        }
    """
    data = request.get_json()

    required_fields = ["category", "key", "value", "importance"]
    if not all(field in data for field in required_fields):
        return jsonify({
            "success": False,
            "error": "필수 필드가 누락되었습니다."
        }), 400

    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)
    user_memory.save_memories([data])

    return jsonify({
        "success": True,
        "message": "메모리가 저장되었습니다."
    })


@bp.route("/memory/<user_id>/context", methods=["GET"])
def get_memory_context(user_id):
    """사용자 메모리를 컨텍스트 문자열로 반환"""
    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)
    context = user_memory.get_context_string()

    return jsonify({
        "success": True,
        "context": context
    })


@bp.route("/memory/stats/<user_id>", methods=["GET"])
def get_memory_stats(user_id):
    """사용자 메모리 통계"""
    from app.services.memory_service import UserMemory

    user_memory = UserMemory(user_id)
    memories = user_memory.get_memories()

    # 카테고리별 통계
    by_category = {}
    by_importance = {}

    for mem in memories:
        category = mem.get("category", "기타")
        importance = mem.get("importance", "low")

        by_category[category] = by_category.get(category, 0) + 1
        by_importance[importance] = by_importance.get(importance, 0) + 1

    return jsonify({
        "success": True,
        "total_memories": len(memories),
        "by_category": by_category,
        "by_importance": by_importance
    })
