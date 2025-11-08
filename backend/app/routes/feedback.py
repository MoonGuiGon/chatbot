"""
피드백 API 라우트
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.database_service import get_mongodb

bp = Blueprint("feedback", __name__)


@bp.route("/feedback", methods=["POST"])
def submit_feedback():
    """
    피드백 제출

    Request:
        {
            "conversation_id": "conv-xyz",
            "message_id": "msg-123",
            "query": "부품 ABC-12345의 재고는?",
            "response": "...",
            "feedback_type": "positive|negative|neutral",
            "user_comment": "재고 수량이 다릅니다",
            "user_correction": "실제 재고는 500개",
            "sources_used": [...],
            "llm_config": {...}
        }
    """
    data = request.get_json()

    conversation_id = data.get("conversation_id")
    message_id = data.get("message_id")
    query = data.get("query")
    response = data.get("response")
    feedback_type = data.get("feedback_type")
    user_comment = data.get("user_comment", "")
    user_correction = data.get("user_correction", "")
    sources_used = data.get("sources_used", [])
    llm_config = data.get("llm_config", {})

    if not all([conversation_id, query, response, feedback_type]):
        return jsonify({
            "success": False,
            "error": "필수 필드가 누락되었습니다."
        }), 400

    # 피드백 저장
    mongodb = get_mongodb()
    feedback_id = mongodb.insert_one("feedback", {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "query": query,
        "response": response,
        "feedback_type": feedback_type,
        "user_comment": user_comment,
        "user_correction": user_correction,
        "sources_used": sources_used,
        "llm_config": llm_config,
        "created_at": datetime.now().isoformat()
    })

    return jsonify({
        "success": True,
        "feedback_id": feedback_id,
        "message": "피드백이 저장되었습니다."
    })


@bp.route("/feedback/stats", methods=["GET"])
def get_feedback_stats():
    """피드백 통계 조회"""
    mongodb = get_mongodb()

    # 전체 피드백 개수
    all_feedback = mongodb.find("feedback", {})

    positive = len([f for f in all_feedback if f.get("feedback_type") == "positive"])
    negative = len([f for f in all_feedback if f.get("feedback_type") == "negative"])
    neutral = len([f for f in all_feedback if f.get("feedback_type") == "neutral"])

    return jsonify({
        "success": True,
        "stats": {
            "total": len(all_feedback),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "satisfaction_rate": positive / len(all_feedback) if all_feedback else 0
        }
    })


@bp.route("/feedback/recent", methods=["GET"])
def get_recent_feedback():
    """최근 피드백 조회"""
    limit = int(request.args.get("limit", 20))

    mongodb = get_mongodb()
    feedback_list = mongodb.find("feedback", {}, limit=limit)

    return jsonify({
        "success": True,
        "feedback": feedback_list
    })


@bp.route("/feedback/improvements", methods=["GET"])
def get_improvement_suggestions():
    """
    피드백 기반 개선 제안
    부정적 피드백에서 패턴 추출
    """
    mongodb = get_mongodb()
    negative_feedback = mongodb.find("feedback", {"feedback_type": "negative"}, limit=100)

    # 간단한 분석
    common_issues = {}
    for feedback in negative_feedback:
        comment = feedback.get("user_comment", "")
        if "재고" in comment:
            common_issues["재고 정보 오류"] = common_issues.get("재고 정보 오류", 0) + 1
        if "느리" in comment or "속도" in comment:
            common_issues["응답 속도"] = common_issues.get("응답 속도", 0) + 1
        if "정확" in comment or "틀리" in comment:
            common_issues["정확도"] = common_issues.get("정확도", 0) + 1

    suggestions = [
        {"issue": issue, "count": count}
        for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True)
    ]

    return jsonify({
        "success": True,
        "suggestions": suggestions
    })
