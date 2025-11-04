"""
Ontology Service - Neo4j Knowledge Graph
"""
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase

from app.config import settings

logger = logging.getLogger(__name__)


class OntologyService:
    """
    Knowledge Graph service using Neo4j
    Stores relationships between entities (parts, documents, suppliers, equipment)
    """

    def __init__(self):
        self.driver = None
        self.use_mock = True

    def initialize(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Neo4j connection"""
        try:
            uri = uri or settings.neo4j_uri if hasattr(settings, 'neo4j_uri') else None
            username = username or settings.neo4j_username if hasattr(settings, 'neo4j_username') else None
            password = password or settings.neo4j_password if hasattr(settings, 'neo4j_password') else None

            if not uri:
                logger.info("Neo4j not configured. Using mock knowledge graph.")
                return

            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")

            self.use_mock = False
            logger.info("Neo4j ontology service initialized")

            # Create indexes
            self._create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            logger.info("Knowledge graph features will use mock data")
            self.use_mock = True

    def _create_indexes(self):
        """Create necessary indexes"""
        if self.use_mock:
            return

        with self.driver.session() as session:
            # Create indexes for fast lookups
            indexes = [
                "CREATE INDEX material_id IF NOT EXISTS FOR (m:Material) ON (m.materialId)",
                "CREATE INDEX document_source IF NOT EXISTS FOR (d:Document) ON (d.source)",
                "CREATE INDEX supplier_name IF NOT EXISTS FOR (s:Supplier) ON (s.name)",
                "CREATE INDEX equipment_id IF NOT EXISTS FOR (e:Equipment) ON (e.equipmentId)",
            ]
            for index_query in indexes:
                try:
                    session.run(index_query)
                except:
                    pass  # Index might already exist

    def add_material_node(self, material_data: Dict[str, Any]):
        """Add or update material node"""
        if self.use_mock:
            logger.info(f"Mock: Would add material node {material_data.get('materialId')}")
            return

        with self.driver.session() as session:
            session.run(
                """
                MERGE (m:Material {materialId: $materialId})
                SET m.name = $name,
                    m.category = $category,
                    m.updated_at = datetime()
                """,
                materialId=material_data.get('materialId'),
                name=material_data.get('name'),
                category=material_data.get('category')
            )

    def add_document_node(self, doc_metadata: Dict[str, Any]):
        """Add document node"""
        if self.use_mock:
            logger.info(f"Mock: Would add document node {doc_metadata.get('source')}")
            return

        with self.driver.session() as session:
            session.run(
                """
                MERGE (d:Document {source: $source})
                SET d.type = $type,
                    d.date = $date,
                    d.updated_at = datetime()
                """,
                source=doc_metadata.get('source'),
                type=doc_metadata.get('type'),
                date=doc_metadata.get('date')
            )

    def create_relationship(
        self,
        from_label: str,
        from_key: str,
        from_value: str,
        to_label: str,
        to_key: str,
        to_value: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Create relationship between two nodes"""
        if self.use_mock:
            logger.info(f"Mock: Would create relationship {from_label}-[{relationship_type}]->{to_label}")
            return

        with self.driver.session() as session:
            query = f"""
                MATCH (a:{from_label} {{{from_key}: $from_value}})
                MATCH (b:{to_label} {{{to_key}: $to_value}})
                MERGE (a)-[r:{relationship_type}]->(b)
                """

            if properties:
                set_clause = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
                query += f"SET {set_clause}"

            params = {
                'from_value': from_value,
                'to_value': to_value
            }
            if properties:
                params.update(properties)

            session.run(query, **params)

    def find_related_entities(
        self,
        entity_type: str,
        entity_key: str,
        entity_value: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Find related entities in the knowledge graph"""
        if self.use_mock:
            return self._mock_related_entities(entity_value)

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (start:{entity_type} {{{entity_key}: $value}})
                CALL apoc.path.subgraphAll(start, {{
                    maxLevel: $max_depth
                }})
                YIELD nodes, relationships
                UNWIND nodes AS node
                RETURN DISTINCT
                    labels(node)[0] AS type,
                    properties(node) AS properties
                LIMIT 50
                """,
                value=entity_value,
                max_depth=max_depth
            )

            entities = []
            for record in result:
                entities.append({
                    'type': record['type'],
                    'properties': dict(record['properties'])
                })

            return entities

    def get_material_context(self, material_id: str) -> Dict[str, Any]:
        """Get comprehensive context for a material from knowledge graph"""
        if self.use_mock:
            return self._mock_material_context(material_id)

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Material {materialId: $material_id})
                OPTIONAL MATCH (m)-[:SUPPLIED_BY]->(s:Supplier)
                OPTIONAL MATCH (m)-[:USED_IN]->(e:Equipment)
                OPTIONAL MATCH (m)-[:DOCUMENTED_IN]->(d:Document)
                OPTIONAL MATCH (m)-[:SIMILAR_TO]->(similar:Material)
                RETURN m,
                       collect(DISTINCT s) AS suppliers,
                       collect(DISTINCT e) AS equipment,
                       collect(DISTINCT d) AS documents,
                       collect(DISTINCT similar) AS similar_materials
                """,
                material_id=material_id
            )

            record = result.single()
            if not record:
                return {}

            return {
                'material': dict(record['m']),
                'suppliers': [dict(s) for s in record['suppliers'] if s],
                'equipment': [dict(e) for e in record['equipment'] if e],
                'documents': [dict(d) for d in record['documents'] if d],
                'similar_materials': [dict(m) for m in record['similar_materials'] if m]
            }

    def _mock_related_entities(self, entity_value: str) -> List[Dict[str, Any]]:
        """Return mock related entities"""
        return [
            {
                'type': 'Supplier',
                'properties': {
                    'name': '샘플 공급업체',
                    'contact': '02-1234-5678'
                }
            },
            {
                'type': 'Equipment',
                'properties': {
                    'equipmentId': 'EQ-001',
                    'name': '반도체 장비 A'
                }
            },
            {
                'type': 'Document',
                'properties': {
                    'source': '부품사양서_MAT001.docx',
                    'type': 'specification'
                }
            }
        ]

    def _mock_material_context(self, material_id: str) -> Dict[str, Any]:
        """Return mock material context"""
        return {
            'material': {
                'materialId': material_id,
                'name': f'부품 {material_id}',
                'category': '전자부품'
            },
            'suppliers': [
                {'name': '샘플 공급업체', 'reliability': 'A급'}
            ],
            'equipment': [
                {'equipmentId': 'EQ-001', 'name': '장비 A'},
                {'equipmentId': 'EQ-002', 'name': '장비 B'}
            ],
            'documents': [
                {'source': '부품사양서.pdf', 'type': 'specification'},
                {'source': '품질관리기준.pdf', 'type': 'quality_standard'}
            ],
            'similar_materials': [
                {'materialId': 'MAT-002', 'name': '유사 부품 A'},
                {'materialId': 'MAT-003', 'name': '유사 부품 B'}
            ]
        }

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()


# Global instance
ontology_service = OntologyService()
