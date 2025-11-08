"""
LLM 서비스
사내 LLM 연동 및 Mock LLM 제공
"""
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.config import config


class RealChatLLM:
    """실제 사내 Chat LLM"""

    def __init__(self, model: str, temperature: float = 0.1, max_tokens: int = 2000):
        self.llm = ChatOpenAI(
            base_url=config.llm.chat_url,
            api_key=config.llm.api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def invoke(self, prompt: str):
        """LLM 호출"""
        return self.llm.invoke(prompt)


class RealEmbeddingLLM:
    """실제 사내 Embedding LLM"""

    def __init__(self, model: str):
        self.embeddings = OpenAIEmbeddings(
            base_url=config.llm.embedding_url,
            api_key=config.llm.api_key,
            model=model
        )

    def embed_query(self, text: str) -> List[float]:
        """텍스트를 벡터로 변환"""
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 벡터로 변환"""
        return self.embeddings.embed_documents(texts)


class RealVisionLLM:
    """실제 사내 Vision LLM"""

    def __init__(self, model: str):
        self.llm = ChatOpenAI(
            base_url=config.llm.vision_url,
            api_key=config.llm.api_key,
            model=model
        )

    def analyze_image(self, image_path: str, prompt: str = "") -> Dict[str, Any]:
        """이미지 분석"""
        # Vision API 호출 로직
        # 실제 구현 시 이미지를 base64로 인코딩하여 전송
        pass


class LLMFactory:
    """
    LLM 팩토리
    테스트 모드에 따라 Mock 또는 실제 LLM 반환
    """

    @staticmethod
    def create_chat_llm(
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Chat LLM 생성"""
        if config.test_mode:
            # 테스트 모드: Mock LLM 사용
            from tests.mocks import MockLLMFactory
            return MockLLMFactory.create_chat_llm(config)

        # 실제 모드: 사내 LLM 사용
        return RealChatLLM(
            model=model or config.llm.chat_model,
            temperature=temperature if temperature is not None else config.llm.temperature,
            max_tokens=max_tokens or config.llm.max_tokens
        )

    @staticmethod
    def create_embedding_llm(model: Optional[str] = None):
        """Embedding LLM 생성"""
        if config.test_mode:
            from tests.mocks import MockLLMFactory
            return MockLLMFactory.create_embedding_llm(config)

        return RealEmbeddingLLM(
            model=model or config.llm.embedding_model
        )

    @staticmethod
    def create_vision_llm(model: Optional[str] = None):
        """Vision LLM 생성"""
        if config.test_mode:
            from tests.mocks import MockLLMFactory
            return MockLLMFactory.create_vision_llm(config)

        return RealVisionLLM(
            model=model or config.llm.vision_model
        )


# 전역 LLM 인스턴스 (싱글톤처럼 사용)
_chat_llm = None
_embedding_llm = None
_vision_llm = None


def get_chat_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
):
    """Chat LLM 인스턴스 반환"""
    global _chat_llm
    if _chat_llm is None or model or temperature or max_tokens:
        _chat_llm = LLMFactory.create_chat_llm(model, temperature, max_tokens)
    return _chat_llm


def get_embedding_llm(model: Optional[str] = None):
    """Embedding LLM 인스턴스 반환"""
    global _embedding_llm
    if _embedding_llm is None or model:
        _embedding_llm = LLMFactory.create_embedding_llm(model)
    return _embedding_llm


def get_vision_llm(model: Optional[str] = None):
    """Vision LLM 인스턴스 반환"""
    global _vision_llm
    if _vision_llm is None or model:
        _vision_llm = LLMFactory.create_vision_llm(model)
    return _vision_llm


def generate_title(messages: List[Dict[str, Any]]) -> str:
    """
    대화 내용을 기반으로 제목 자동 생성

    제목 생성 전략:
    1. 첫 사용자 메시지가 질문이면 요약 (30자 이내)
    2. 첫 3개 메시지를 보고 LLM이 핵심 주제 추출
    3. 간결하고 명확한 제목 (한국어, 30자 이내)

    Args:
        messages: 대화 메시지 목록 [{"role": "user/assistant", "content": "..."}]

    Returns:
        생성된 제목 (예: "부품 ABC-12345 재고 조회")
    """
    if not messages:
        return "새 대화"

    # 첫 번째 사용자 메시지 추출
    first_user_message = None
    for msg in messages:
        if msg.get("role") == "user":
            first_user_message = msg.get("content", "")
            break

    if not first_user_message:
        return "새 대화"

    # 간단한 경우: 첫 메시지가 짧으면 그대로 사용
    if len(first_user_message) <= 30:
        return first_user_message

    # LLM을 사용하여 제목 생성
    llm = get_chat_llm(temperature=0.3)  # 창의성 약간 높임

    # 처음 최대 3개 메시지 사용
    context_messages = messages[:min(6, len(messages))]  # user+assistant 3턴
    context = "\n".join([
        f"{'사용자' if msg.get('role') == 'user' else '봇'}: {msg.get('content', '')[:200]}"
        for msg in context_messages
    ])

    prompt = f"""다음 대화의 핵심 주제를 30자 이내의 간결한 제목으로 만들어주세요.

대화 내용:
{context}

제목 생성 규칙:
- 30자 이내로 간결하게
- 핵심 키워드 포함 (부품 번호, 작업 내용 등)
- 의문형이 아닌 명사형으로
- 특수문자 사용 안함

예시:
- "부품 ABC-12345 재고 조회"
- "라인 1 검사 이력 확인"
- "출고 현황 분석"

제목:"""

    try:
        response = llm.invoke(prompt)
        title = response.content.strip()

        # 제목 정제
        title = title.replace('"', '').replace("'", '').strip()

        # 30자 제한
        if len(title) > 30:
            title = title[:27] + "..."

        return title if title else "새 대화"

    except Exception as e:
        print(f"제목 생성 오류: {e}")
        # 실패 시 첫 메시지의 앞부분 사용
        return first_user_message[:27] + "..." if len(first_user_message) > 30 else first_user_message
