"""
Configuration module for the chatbot application
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    mongodb_uri: str = "mongodb://localhost:27017/"
    mongodb_db_name: str = "chatbot_db"
    postgres_uri: str = "postgresql://user:password@localhost:5432/chatbot_db"

    # LLM Configuration
    llm_api_key: str = ""
    llm_api_url: str = ""
    llm_model_name: str = ""
    llm_embedding_model: str = ""
    llm_vision_model: str = ""

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
