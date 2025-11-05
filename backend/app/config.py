"""
Configuration module for the chatbot application
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db_name: str = "chatbot_db"
    postgres_uri: str = "postgresql://user:password@localhost:5432/chatbot_db"

    # Chat Model Configuration (대화용)
    chat_api_key: str = ""
    chat_api_url: str = ""
    chat_model_name: str = ""

    # Embedding Model Configuration (벡터 임베딩용)
    embedding_api_key: str = ""
    embedding_api_url: str = ""
    embedding_model_name: str = ""

    # Vision Model Configuration (이미지 분석용)
    vision_api_key: str = ""
    vision_api_url: str = ""
    vision_model_name: str = ""

    # VectorDB (pgvector)
    vectordb_type: str = "pgvector"
    vectordb_path: str = "./vectordb_data"

    # Neo4j (OntologyDB)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""

    # Redis (Cache)
    redis_url: str = "redis://localhost:6379"

    # Flask
    flask_env: str = "development"
    flask_debug: bool = True
    secret_key: str = "dev-secret-key"
    port: int = 5000

    # CORS
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
