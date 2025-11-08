"""
채팅 API 라우트
"""
from flask import Blueprint, request, jsonify, Response
import json
from app.agents.chatbot_agent import get_chatbot_agent
from app.services.database_service import get_mongodb

bp = Blueprint("chat", __name__)


@bp.route("/chat", methods=["POST"])
def chat():
    """
    채팅 메시지 처리 (동기)

    Request:
        {
            "message": "부품 ABC-12345의 재고는?",
            "user_id": "user123",
            "conversation_id": "conv-xyz",
            "custom_prompt": "...",  # Optional
            "llm_config": {  # Optional
                "model": "gpt-4",
                "temperature": 0.1
            }
        }

    Response:
        {
            "success": true,
            "content": "...",
            "sources": [...],
            "confidence_score": 0.85,
            "table_data": [...],
            "chart_data": {...},
            "warnings": [...]
        }
    """
    data = request.get_json()

    message = data.get("message")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    custom_prompt = data.get("custom_prompt")
    llm_config = data.get("llm_config")

    if not message:
        return jsonify({"success": False, "error": "메시지가 필요합니다."}), 400

    # 챗봇 실행
    agent = get_chatbot_agent()
    result = agent.invoke(
        query=message,
        user_id=user_id,
        conversation_id=conversation_id,
        custom_prompt=custom_prompt,
        llm_config=llm_config
    )

    # 대화 저장 (MongoDB)
    if result.get("success") and conversation_id:
        from datetime import datetime
        from app.services.llm_service import generate_title

        mongodb = get_mongodb()

        # 사용자 메시지 추가
        mongodb.update_one(
            "conversations",
            {"conversation_id": conversation_id},
            {
                "$push": {
                    "messages": {
                        "role": "user",
                        "content": message,
                        "timestamp": datetime.utcnow()
                    }
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # 봇 응답 추가
        mongodb.update_one(
            "conversations",
            {"conversation_id": conversation_id},
            {
                "$push": {
                    "messages": {
                        "role": "assistant",
                        "content": result.get("content"),
                        "sources": result.get("sources"),
                        "confidence_score": result.get("confidence_score"),
                        "timestamp": datetime.utcnow()
                    }
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # 첫 메시지 후 자동으로 제목 생성
        conversation = mongodb.find_one("conversations", {"conversation_id": conversation_id})
        if conversation:
            messages = conversation.get("messages", [])
            # 첫 번째 사용자 메시지 후 (총 2개 메시지) 제목 자동 생성
            if len(messages) == 2 and conversation.get("title") == "새 대화":
                title = generate_title(messages)
                mongodb.update_one(
                    "conversations",
                    {"conversation_id": conversation_id},
                    {"$set": {"title": title}}
                )
                result["conversation_title"] = title

    return jsonify(result)


@bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """
    채팅 메시지 처리 (스트리밍)
    Server-Sent Events (SSE) 방식
    """
    data = request.get_json()

    message = data.get("message")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    custom_prompt = data.get("custom_prompt")
    llm_config = data.get("llm_config")

    if not message:
        return jsonify({"success": False, "error": "메시지가 필요합니다."}), 400

    def generate():
        """SSE 이벤트 스트림 생성"""
        agent = get_chatbot_agent()

        for event in agent.stream(
            query=message,
            user_id=user_id,
            conversation_id=conversation_id,
            custom_prompt=custom_prompt,
            llm_config=llm_config
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@bp.route("/conversations", methods=["GET"])
def get_conversations():
    """사용자의 대화 목록 조회"""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id가 필요합니다."}), 400

    mongodb = get_mongodb()
    conversations = mongodb.find("conversations", {"user_id": user_id}, limit=50)

    return jsonify({
        "success": True,
        "conversations": conversations
    })


@bp.route("/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """특정 대화 조회"""
    mongodb = get_mongodb()
    conversation = mongodb.find_one("conversations", {"conversation_id": conversation_id})

    if not conversation:
        return jsonify({"success": False, "error": "대화를 찾을 수 없습니다."}), 404

    return jsonify({
        "success": True,
        "conversation": conversation
    })


@bp.route("/conversations", methods=["POST"])
def create_conversation():
    """새 대화 생성"""
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id가 필요합니다."}), 400

    import uuid
    from datetime import datetime
    conversation_id = f"conv_{uuid.uuid4().hex[:12]}"

    mongodb = get_mongodb()
    mongodb.insert_one("conversations", {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "title": "새 대화",  # 기본 제목
        "messages": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return jsonify({
        "success": True,
        "conversation_id": conversation_id,
        "title": "새 대화"
    })


@bp.route("/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """대화 삭제"""
    mongodb = get_mongodb()

    # 대화 존재 확인
    conversation = mongodb.find_one("conversations", {"conversation_id": conversation_id})
    if not conversation:
        return jsonify({"success": False, "error": "대화를 찾을 수 없습니다."}), 404

    # 삭제
    mongodb.delete_one("conversations", {"conversation_id": conversation_id})

    return jsonify({
        "success": True,
        "message": "대화가 삭제되었습니다."
    })


@bp.route("/conversations/<conversation_id>/title", methods=["PUT"])
def update_conversation_title(conversation_id):
    """대화 제목 수정"""
    data = request.get_json()
    new_title = data.get("title")

    if not new_title:
        return jsonify({"success": False, "error": "제목이 필요합니다."}), 400

    from datetime import datetime
    mongodb = get_mongodb()

    # 대화 존재 확인
    conversation = mongodb.find_one("conversations", {"conversation_id": conversation_id})
    if not conversation:
        return jsonify({"success": False, "error": "대화를 찾을 수 없습니다."}), 404

    # 제목 업데이트
    mongodb.update_one(
        "conversations",
        {"conversation_id": conversation_id},
        {
            "$set": {
                "title": new_title,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return jsonify({
        "success": True,
        "title": new_title
    })


@bp.route("/conversations/<conversation_id>/generate-title", methods=["POST"])
def generate_conversation_title(conversation_id):
    """
    대화 내용을 기반으로 LLM이 자동으로 제목 생성

    제목 생성 로직:
    1. 첫 사용자 메시지 기반 (간단한 경우)
    2. 처음 3개 메시지 요약 (LLM 사용)
    3. 최대 30자 이내로 간결하게
    """
    from datetime import datetime
    from app.services.llm_service import generate_title

    mongodb = get_mongodb()

    # 대화 조회
    conversation = mongodb.find_one("conversations", {"conversation_id": conversation_id})
    if not conversation:
        return jsonify({"success": False, "error": "대화를 찾을 수 없습니다."}), 404

    messages = conversation.get("messages", [])
    if len(messages) == 0:
        return jsonify({"success": False, "error": "메시지가 없어 제목을 생성할 수 없습니다."}), 400

    # 제목 생성
    title = generate_title(messages)

    # 제목 업데이트
    mongodb.update_one(
        "conversations",
        {"conversation_id": conversation_id},
        {
            "$set": {
                "title": title,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return jsonify({
        "success": True,
        "title": title
    })
