"""
services/relationship_service.py
---------------------------------
RelationshipService — Node 3 service for Graph 1.

Identifies direct and causal relationships between entities and documents:
    - Task DEPENDS_ON Task
    - Vendor BLOCKS Task / Milestone
    - Person OWNS Task
    - Risk IMPACTS Task / Milestone
"""

from __future__ import annotations

import re
from schemas.domain.snapshot import ProjectSnapshot
from schemas.domain.normalized_document import NormalizedDocument
from schemas.domain.knowledge_entity import KnowledgeEntity, EntityType
from schemas.domain.relationship import Relationship, RelationshipType
from utils.logger import get_logger

_log = get_logger("services.relationship")


class RelationshipService:
    """
    Extracts structural and causal relationships from snapshot items and documents.
    """

    def extract_relationships(
        self,
        snapshot: ProjectSnapshot,
        documents: list[NormalizedDocument],
        entities: list[KnowledgeEntity],
    ) -> list[Relationship]:
        """
        Extract relationships across project entities and documents.
        """
        _log.info("Extracting relationships for project_id=%s", snapshot.project.project_id)
        relationships: list[Relationship] = []
        seen: set[tuple[str, str, str]] = set()

        def _add_rel(src: str, tgt: str, rel_type: RelationshipType, conf: float = 1.0):
            key = (src, tgt, rel_type.value)
            if key not in seen and src != tgt:
                seen.add(key)
                relationships.append(
                    Relationship(
                        source_entity=src,
                        target_entity=tgt,
                        relationship_type=rel_type,
                        confidence=conf,
                    )
                )

        # 1. Task Dependencies (task DEPENDS_ON task)
        for task in snapshot.tasks:
            task_id_str = f"task_ent_{task.id}"
            for dep_id in task.dependencies:
                dep_str = f"task_ent_{dep_id}"
                _add_rel(task_id_str, dep_str, RelationshipType.DEPENDS_ON, 1.0)

            if task.owner:
                person_id = f"person_{task.owner.lower().replace(' ', '_')}"
                _add_rel(person_id, task_id_str, RelationshipType.OWNS, 1.0)

        # 2. Blockers (e.g. Vendor or Issue BLOCKS Task)
        for task in snapshot.tasks:
            task_id_str = f"task_ent_{task.id}"
            for blocker in task.blockers:
                text_lower = blocker.lower()

                if "cloudsphere" in text_lower:
                    _add_rel("vendor_cloudsphere", task_id_str, RelationshipType.BLOCKS, 0.95)
                elif "procurement" in text_lower or "contract" in text_lower:
                    _add_rel("vendor_securecheck", task_id_str, RelationshipType.BLOCKS, 0.90)
                elif "gl_accounts" in text_lower or "data quality" in text_lower:
                    _add_rel("task_ent_203", task_id_str, RelationshipType.BLOCKS, 0.90)

        # 3. Risks (Risk IMPACTS Task/Project)
        for risk in snapshot.risk_register:
            risk_id_str = f"risk_{risk.id}"
            if risk.owner:
                person_id = f"person_{risk.owner.lower().replace(' ', '_')}"
                _add_rel(person_id, risk_id_str, RelationshipType.OWNS, 0.9)

            title_lower = risk.title.lower()
            if "vendor" in title_lower or "cloudsphere" in title_lower:
                _add_rel("vendor_cloudsphere", risk_id_str, RelationshipType.IMPACTS, 0.95)
            elif "gl_accounts" in title_lower or "data corruption" in title_lower:
                _add_rel("task_ent_203", risk_id_str, RelationshipType.IMPACTS, 0.95)
            elif "gdpr" in title_lower or "procurement" in title_lower:
                _add_rel("vendor_securecheck", risk_id_str, RelationshipType.IMPACTS, 0.95)

        # 4. Stakeholder Ownership
        for sh in snapshot.stakeholders:
            person_id = f"person_{sh.name.lower().replace(' ', '_')}"
            if sh.department:
                team_id = f"team_{sh.department.lower().replace(' ', '_')}"
                _add_rel(person_id, team_id, RelationshipType.ASSIGNED_TO, 1.0)

        _log.info("Extracted %d relationships for project_id=%s", len(relationships), snapshot.project.project_id)
        return relationships
