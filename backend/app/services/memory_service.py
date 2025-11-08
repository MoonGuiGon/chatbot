"""
메모리 서비스
- 단기 메모리: 현재 대화 컨텍스트 유지
- 장기 메모리: 사용자별 중요 정보 저장
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from app.services.database_service import get_mongodb
from app.services.llm_service import get_chat_llm


class ConversationMemory:
    """
    단기 메모리: 현재 대화의 컨텍스트 유지
    """

    def __init__(self, conversation_id: str, max_messages: int = 10):
        self.conversation_id = conversation_id
        self.max_messages = max_messages
        self.messages = []

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """메시지 추가"""
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

        # 최대 메시지 수 제한
        if len(self.messages) > self.max_messages * 2:  # user + assistant = 2
            self.messages = self.messages[-self.max_messages * 2:]

    def get_context(self) -> str:
        """현재 대화 컨텍스트를 문자열로 반환"""
        if not self.messages:
            return ""

        context_parts = ["=== 이전 대화 내용 ==="]
        for msg in self.messages[-10:]:  # 최근 10개 메시지
            role = "사용자" if msg["role"] == "user" else "챗봇"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)

    def get_messages(self) -> List[Dict[str, Any]]:
        """전체 메시지 반환"""
        return self.messages


class UserMemory:
    """
    장기 메모리: 사용자별 중요 정보 저장
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.mongodb = get_mongodb()
        self.collection = "user_memories"

    def extract_important_info(self, conversation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        대화에서 중요한 정보 추출
        LLM을 사용하여 자동으로 중요 정보 식별
        """
        if not conversation:
            return []

        # 대화 내용 준비
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation[-10:]  # 최근 10개 메시지만
        ])

        # LLM에게 중요 정보 추출 요청
        llm = get_chat_llm()
        prompt = f"""
다음 대화에서 사용자에 대해 기억해야 할 중요한 정보를 추출하세요.

대화 내용:
{conversation_text}

중요 정보 추출 기준:
1. 사용자의 선호도 (예: 특정 부품 관심, 선호하는 응답 형식)
2. 사용자의 역할/부서 (예: 생산팀, 품질팀)
3. 자주 조회하는 부품이나 정보
4. 사용자가 명시적으로 기억해달라고 한 내용
5. 업무와 관련된 중요한 컨텍스트

JSON 배열로 반환하세요:
[
  {{
    "category": "선호도|역할|자주조회|명시적요청|업무컨텍스트",
    "key": "짧은 키워드",
    "value": "실제 내용",
    "importance": "high|medium|low"
  }}
]

중요한 정보가 없으면 빈 배열 []을 반환하세요.
JSON만 출력하세요:
"""

        try:
            response = llm.invoke(prompt)
            memories = json.loads(response.content)

            # 유효성 검증
            if isinstance(memories, list):
                return [
                    mem for mem in memories
                    if isinstance(mem, dict) and all(
                        k in mem for k in ["category", "key", "value", "importance"]
                    )
                ]
        except Exception as e:
            print(f"Memory extraction error: {e}")

        return []

    def save_memories(self, memories: List[Dict[str, Any]]):
        """메모리 저장"""
        if not memories:
            return

        for memory in memories:
            # 기존 메모리 업데이트 또는 새로 저장
            self.mongodb.update_one(
                self.collection,
                {
                    "user_id": self.user_id,
                    "category": memory["category"],
                    "key": memory["key"]
                },
                {
                    "$set": {
                        "user_id": self.user_id,
                        "category": memory["category"],
                        "key": memory["key"],
                        "value": memory["value"],
                        "importance": memory["importance"],
                        "updated_at": datetime.now().isoformat()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.now().isoformat()
                    }
                }
            )

    def get_memories(self, category: Optional[str] = None, importance: Optional[str] = None) -> List[Dict[str, Any]]:
        """저장된 메모리 조회"""
        query = {"user_id": self.user_id}

        if category:
            query["category"] = category

        if importance:
            query["importance"] = importance

        memories = self.mongodb.find(self.collection, query, limit=50)
        return memories

    def get_context_string(self) -> str:
        """메모리를 컨텍스트 문자열로 변환"""
        memories = self.get_memories()

        if not memories:
            return ""

        # 중요도별 정렬
        importance_order = {"high": 0, "medium": 1, "low": 2}
        memories.sort(key=lambda x: importance_order.get(x.get("importance", "low"), 3))

        context_parts = ["=== 사용자에 대해 알고 있는 정보 ==="]

        # 카테고리별로 그룹화
        by_category = {}
        for mem in memories[:10]:  # 최대 10개
            category = mem.get("category", "기타")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(mem)

        category_names = {
            "선호도": "사용자 선호도",
            "역할": "사용자 역할/부서",
            "자주조회": "자주 조회하는 정보",
            "명시적요청": "기억해달라고 요청한 내용",
            "업무컨텍스트": "업무 컨텍스트"
        }

        for category, mems in by_category.items():
            context_parts.append(f"\n[{category_names.get(category, category)}]")
            for mem in mems:
                context_parts.append(f"- {mem['key']}: {mem['value']}")

        return "\n".join(context_parts)

    def delete_memory(self, memory_id: str):
        """특정 메모리 삭제"""
        self.mongodb.delete_one(self.collection, {"_id": memory_id, "user_id": self.user_id})

    def clear_all_memories(self):
        """모든 메모리 삭제 (사용자 요청 시)"""
        # 실제로는 삭제하지 않고 archived로 표시
        memories = self.get_memories()
        for mem in memories:
            self.mongodb.update_one(
                self.collection,
                {"_id": mem["_id"]},
                {"$set": {"archived": True, "archived_at": datetime.now().isoformat()}}
            )


class MemoryManager:
    """
    메모리 매니저
    단기 메모리(대화 컨텍스트)와 장기 메모리(사용자 정보)를 통합 관리
    """

    def __init__(self, user_id: str, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.conversation_memory = ConversationMemory(conversation_id)
        self.user_memory = UserMemory(user_id)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """메시지 추가 (단기 메모리)"""
        self.conversation_memory.add_message(role, content, metadata)

    def get_full_context(self) -> str:
        """
        전체 컨텍스트 반환 (단기 + 장기)
        LLM 프롬프트에 포함될 컨텍스트
        """
        contexts = []

        # 1. 장기 메모리 (사용자에 대한 정보)
        user_context = self.user_memory.get_context_string()
        if user_context:
            contexts.append(user_context)

        # 2. 단기 메모리 (현재 대화)
        conversation_context = self.conversation_memory.get_context()
        if conversation_context:
            contexts.append(conversation_context)

        return "\n\n".join(contexts)

    def save_conversation_memories(self):
        """
        대화 종료 시 중요 정보 추출 및 저장
        - 대화가 길어지면 자동으로 호출
        - 사용자가 명시적으로 요청하면 호출
        """
        messages = self.conversation_memory.get_messages()

        if len(messages) < 2:  # 최소 1턴 이상
            return

        # 중요 정보 추출
        important_info = self.user_memory.extract_important_info(messages)

        # 저장
        if important_info:
            self.user_memory.save_memories(important_info)
            return len(important_info)

        return 0

    def get_user_memories(self) -> List[Dict[str, Any]]:
        """사용자 메모리 조회 (UI에서 표시용)"""
        return self.user_memory.get_memories()

    def delete_user_memory(self, memory_id: str):
        """특정 메모리 삭제"""
        self.user_memory.delete_memory(memory_id)

    def clear_all_user_memories(self):
        """모든 사용자 메모리 삭제"""
        self.user_memory.clear_all_memories()


# 전역 메모리 관리자 캐시
_memory_managers = {}


def get_memory_manager(user_id: str, conversation_id: str) -> MemoryManager:
    """메모리 매니저 인스턴스 반환 (캐싱)"""
    key = f"{user_id}:{conversation_id}"

    if key not in _memory_managers:
        _memory_managers[key] = MemoryManager(user_id, conversation_id)

    return _memory_managers[key]


def cleanup_memory_cache(conversation_id: str):
    """대화 종료 시 캐시에서 제거"""
    keys_to_remove = [k for k in _memory_managers.keys() if conversation_id in k]
    for key in keys_to_remove:
        del _memory_managers[key]
