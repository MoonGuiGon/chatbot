import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """사내 LLM 설정"""
    chat_url: str = os.getenv("LLM_CHAT_URL", "https://common.llm.com/v1/chat/completions")
    embedding_url: str = os.getenv("LLM_EMBEDDING_URL", "https://embedding.llm.com/v1/embeddings")
    vision_url: str = os.getenv("LLM_VISION_URL", "https://vision.llm.com/v1/chat/completions")
    api_key: str = os.getenv("LLM_API_KEY", "")

    # 기본 모델 설정
    chat_model: str = os.getenv("LLM_CHAT_MODEL", "gpt-4")
    embedding_model: str = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-ada-002")
    vision_model: str = os.getenv("LLM_VISION_MODEL", "gpt-4-vision")

    # 기본 파라미터
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))


@dataclass
class DatabaseConfig:
    """데이터베이스 설정"""
    # MongoDB
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "semiconductor_chatbot")

    # PostgreSQL (pgvector)
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_database: str = os.getenv("POSTGRES_DATABASE", "vectordb")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")

    @property
    def postgres_uri(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"


@dataclass
class AppConfig:
    """애플리케이션 전체 설정"""
    # Flask 설정
    flask_env: str = os.getenv("FLASK_ENV", "development")
    flask_debug: bool = os.getenv("FLASK_DEBUG", "True") == "True"
    flask_port: int = int(os.getenv("FLASK_PORT", "5000"))

    # 테스트 모드 (DB, LLM을 Mock으로 대체)
    test_mode: bool = os.getenv("TEST_MODE", "False") == "True"

    # 파일 업로드 설정
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # MB to bytes
    allowed_extensions: set = field(default_factory=lambda: {"pdf", "ppt", "pptx", "doc", "docx", "xls", "xlsx"})

    # RAG 설정
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k_documents: int = int(os.getenv("TOP_K_DOCUMENTS", "5"))

    # Hallucination 검증 임계값
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

    # 캐시 설정
    enable_cache: bool = os.getenv("ENABLE_CACHE", "True") == "True"
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # seconds

    # LLM & DB 설정
    llm: LLMConfig = field(default_factory=LLMConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)


# 전역 설정 인스턴스
config = AppConfig()
