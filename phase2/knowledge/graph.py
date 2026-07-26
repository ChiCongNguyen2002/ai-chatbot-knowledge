"""
Phase 2 - Knowledge Graph
Build entity-relationship graph for better understanding
"""

from typing import List, Dict, Set, Optional, Tuple
import re


class Entity:
    """Represents an entity in knowledge graph"""

    def __init__(self, name: str, entity_type: str, metadata: Optional[Dict] = None):
        self.name = name
        self.type = entity_type  # 'technology', 'concept', 'pattern', 'service'
        self.metadata = metadata or {}
        self.relations: Dict[str, Set[str]] = {}  # relation_type -> set of entity names

    def add_relation(self, relation_type: str, target_entity: str):
        """Add relationship to another entity"""
        if relation_type not in self.relations:
            self.relations[relation_type] = set()
        self.relations[relation_type].add(target_entity)


class KnowledgeGraph:
    """
    Knowledge graph for Anfin tech stack

    Structure:
    - Entities: microservices, Docker, Kafka, API, etc.
    - Relations: uses, deploys, communicates, depends_on, etc.

    Example:
    microservices --uses--> Docker
    microservices --needs--> API
    Kafka --enables--> microservices
    """

    def __init__(self):
        """Initialize knowledge graph"""
        self.entities: Dict[str, Entity] = {}
        self._build_default_graph()

    def _build_default_graph(self):
        """Build default Anfin tech stack graph"""
        # Define main entities
        entities_data = [
            ('microservices', 'architecture'),
            ('docker', 'technology'),
            ('kubernetes', 'technology'),
            ('kafka', 'technology'),
            ('api', 'pattern'),
            ('database', 'technology'),
            ('cache', 'technology'),
            ('monitoring', 'concept'),
            ('testing', 'concept'),
            ('security', 'concept'),
        ]

        for name, type_ in entities_data:
            self.add_entity(name, type_)

        # Define relationships
        relations = [
            ('microservices', 'uses', 'api'),
            ('microservices', 'deployed_with', 'docker'),
            ('docker', 'orchestrated_by', 'kubernetes'),
            ('microservices', 'communicates_via', 'kafka'),
            ('api', 'needs', 'security'),
            ('microservices', 'needs', 'testing'),
            ('microservices', 'needs', 'monitoring'),
            ('docker', 'stores_in', 'registry'),
            ('kubernetes', 'monitors', 'microservices'),
        ]

        for source, relation, target in relations:
            if source in self.entities and target in self.entities:
                self.add_relation(source, relation, target)

    def add_entity(self, name: str, entity_type: str, metadata: Optional[Dict] = None) -> Entity:
        """Add entity to graph"""
        entity = Entity(name.lower(), entity_type, metadata)
        self.entities[name.lower()] = entity
        return entity

    def add_relation(self, source: str, relation_type: str, target: str) -> bool:
        """Add relationship between entities"""
        source_lower = source.lower()
        target_lower = target.lower()

        if source_lower not in self.entities:
            self.add_entity(source_lower, 'unknown')
        if target_lower not in self.entities:
            self.add_entity(target_lower, 'unknown')

        self.entities[source_lower].add_relation(relation_type, target_lower)
        return True

    def get_related_entities(
        self,
        entity_name: str,
        relation_type: Optional[str] = None,
        depth: int = 1
    ) -> Set[str]:
        """
        Find related entities

        Args:
            entity_name: Starting entity
            relation_type: Filter by relation type (e.g., 'uses', 'deployed_with')
            depth: How many hops to traverse (1 = direct relations only)

        Returns:
            Set of related entity names
        """
        entity_lower = entity_name.lower()

        if entity_lower not in self.entities:
            return set()

        related = set()
        to_visit = [(entity_lower, 0)]  # (entity_name, current_depth)
        visited = set()

        while to_visit:
            current, current_depth = to_visit.pop(0)

            if current in visited or current_depth >= depth:
                continue

            visited.add(current)

            if current in self.entities:
                entity = self.entities[current]

                for rel_type, targets in entity.relations.items():
                    if relation_type is None or rel_type == relation_type:
                        for target in targets:
                            related.add(target)
                            if current_depth < depth - 1:
                                to_visit.append((target, current_depth + 1))

        return related

    def extract_entities_from_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract entities from text

        Args:
            text: Input text

        Returns:
            List of (entity_name, entity_type) tuples found in text
        """
        found = []
        text_lower = text.lower()

        for entity_name, entity in self.entities.items():
            if entity_name in text_lower:
                found.append((entity_name, entity.type))

        return found

    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """
        Find path between two entities (BFS)

        Args:
            start: Starting entity
            end: Target entity

        Returns:
            List of entities in path, or None if no path exists
        """
        start_lower = start.lower()
        end_lower = end.lower()

        if start_lower not in self.entities or end_lower not in self.entities:
            return None

        queue = [(start_lower, [start_lower])]
        visited = {start_lower}

        while queue:
            current, path = queue.pop(0)

            if current == end_lower:
                return path

            if current in self.entities:
                for targets in self.entities[current].relations.values():
                    for target in targets:
                        if target not in visited:
                            visited.add(target)
                            queue.append((target, path + [target]))

        return None

    def get_entity_summary(self, entity_name: str) -> str:
        """Get summary of entity and its relationships"""
        entity_lower = entity_name.lower()

        if entity_lower not in self.entities:
            return f"Entity '{entity_name}' not found in knowledge graph"

        entity = self.entities[entity_lower]
        summary = f"**{entity_lower}** (type: {entity.type})\n\n"
        summary += "Relations:\n"

        if not entity.relations:
            summary += "  (no relations)"
        else:
            for rel_type, targets in entity.relations.items():
                for target in targets:
                    summary += f"  - {rel_type} → {target}\n"

        return summary

    def visualize(self) -> str:
        """Create ASCII visualization of graph"""
        lines = ["Knowledge Graph:\n"]

        for entity_name, entity in sorted(self.entities.items()):
            if entity.relations:
                for rel_type, targets in entity.relations.items():
                    for target in sorted(targets):
                        lines.append(f"  {entity_name} --{rel_type}--> {target}")

        return "\n".join(lines)
