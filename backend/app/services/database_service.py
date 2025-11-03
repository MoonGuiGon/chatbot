"""
Database service for PostgreSQL and MongoDB connections
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import logging

from app.config import settings
from app.models.database import Base

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for PostgreSQL"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def initialize(self, db_uri: Optional[str] = None):
        """Initialize PostgreSQL connection"""
        try:
            uri = db_uri or settings.postgres_uri
            self.engine = create_engine(uri, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Create tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("PostgreSQL database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            # Use in-memory SQLite for testing
            logger.info("Falling back to SQLite in-memory database")
            self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_db(self):
        """Get database session"""
        if self.SessionLocal is None:
            self.initialize()

        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()


class MongoDBService:
    """Database service for MongoDB"""

    def __init__(self):
        self.client = None
        self.db = None

    def initialize(self, mongo_uri: Optional[str] = None, db_name: Optional[str] = None):
        """Initialize MongoDB connection"""
        try:
            uri = mongo_uri or settings.mongodb_uri
            db_name = db_name or settings.mongodb_db_name

            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[db_name]
            logger.info(f"MongoDB connected successfully to database: {db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.info("MongoDB features will be disabled. Using mock data instead.")
            self.client = None
            self.db = None

    def get_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        """Get material by ID"""
        if self.db is None:
            # Return mock data
            return self._get_mock_material(material_id)

        try:
            collection = self.db["materials"]
            material = collection.find_one({"materialId": material_id})
            if material:
                material['_id'] = str(material['_id'])  # Convert ObjectId to string
            return material
        except Exception as e:
            logger.error(f"Error fetching material {material_id}: {e}")
            return None

    def search_materials(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search materials by query"""
        if self.db is None:
            return self._get_mock_materials_list()

        try:
            collection = self.db["materials"]
            materials = list(collection.find(query).limit(limit))
            for material in materials:
                material['_id'] = str(material['_id'])
            return materials
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            return []

    def _get_mock_material(self, material_id: str) -> Dict[str, Any]:
        """Return mock material data for testing"""
        return {
            "materialId": material_id,
            "name": f"반도체 부품 샘플 {material_id}",
            "category": "반도체 장비 부품",
            "specifications": {
                "type": "전자부품",
                "voltage": "220V",
                "size": "10x10x5mm",
                "weight": "50g"
            },
            "supplier": "샘플 공급업체",
            "inventory": {
                "current_stock": 150,
                "minimum_stock": 50,
                "location": "A동 2층 창고"
            },
            "purchase_history": [
                {"date": "2024-01-15", "quantity": 100, "price": 50000},
                {"date": "2024-02-20", "quantity": 200, "price": 45000}
            ],
            "usage_history": [
                {"date": "2024-03-01", "equipment": "EQ-001", "quantity": 5},
                {"date": "2024-03-15", "equipment": "EQ-002", "quantity": 3}
            ],
            "installation_history": [
                {"date": "2024-03-10", "equipment": "EQ-001", "location": "라인 1"},
                {"date": "2024-03-20", "equipment": "EQ-002", "location": "라인 2"}
            ]
        }

    def _get_mock_materials_list(self) -> List[Dict[str, Any]]:
        """Return mock materials list for testing"""
        return [
            self._get_mock_material("MAT-001"),
            self._get_mock_material("MAT-002"),
            self._get_mock_material("MAT-003")
        ]


# Global instances
db_service = DatabaseService()
mongodb_service = MongoDBService()
