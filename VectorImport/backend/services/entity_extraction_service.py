"""
services/entity_extraction_service.py
--------------------------------------
EntityExtractionService — Node 2 service for Graph 1.

Extracts KnowledgeEntity objects (people, teams, vendors, deliverables,
milestones, applications, services, tasks, dependencies) from normalized documents
and snapshot data.
"""

from __future__ import annotations

import re
from typing import Sequence
from schemas.domain.snapshot import ProjectSnapshot
from schemas.domain.normalized_document import NormalizedDocument
from schemas.domain.knowledge_entity import KnowledgeEntity, EntityType
from utils.logger import get_logger

_log = get_logger("services.entity_extraction")

# Known vendor keywords for deterministic extraction
_VENDOR_PATTERNS = [
    r"CloudSphere(?:\s+Inc\.?)?",
    r"SAP(?:\s+AG|\s+S/4HANA)?",
    r"SecureCheck(?:\s+Ltd\.?)?",
    r"TechPartner(?:\s+Inc\.?)?",
    r"CyberProof(?:\s+Ltd\.?)?",
    r"AWS",
    r"Azure",
]


class EntityExtractionService:
    """
    Extracts business entities from normalized documents and snapshot metadata.
    """

    def extract_entities(
        self,
        snapshot: ProjectSnapshot,
        documents: list[NormalizedDocument],
    ) -> list[KnowledgeEntity]:
        """
        Extract unique business entities across snapshot and normalized documents.
        """
        _log.info("Extracting entities for project_id=%s", snapshot.project.project_id)
        entities_map: dict[str, KnowledgeEntity] = {}

        def _add_entity(
            entity_id: str,
            entity_type: EntityType,
            name: str,
            description: str = "",
            doc_id: str | None = None,
        ):
            if entity_id in entities_map:
                existing = entities_map[entity_id]
                doc_ids = list(set(existing.source_document_ids + ([doc_id] if doc_id else [])))
                entities_map[entity_id] = KnowledgeEntity(
                    entity_id=existing.entity_id,
                    entity_type=existing.entity_type,
                    name=existing.name,
                    description=existing.description or description,
                    source_document_ids=doc_ids,
                )
            else:
                entities_map[entity_id] = KnowledgeEntity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    name=name,
                    description=description,
                    source_document_ids=[doc_id] if doc_id else [],
                )

        # 1. Extract People & Teams from Stakeholders
        for sh in snapshot.stakeholders:
            person_id = f"person_{sh.name.lower().replace(' ', '_')}"
            _add_entity(
                entity_id=person_id,
                entity_type=EntityType.PERSON,
                name=sh.name,
                description=f"{sh.role or 'Stakeholder'} - {sh.department or 'General'}",
            )
            if sh.department:
                team_id = f"team_{sh.department.lower().replace(' ', '_')}"
                _add_entity(
                    entity_id=team_id,
                    entity_type=EntityType.TEAM,
                    name=f"{sh.department} Team",
                    description=f"Department team for {sh.department}",
                )

        # 2. Extract Tasks & Dependencies
        for task in snapshot.tasks:
            task_ent_id = f"task_ent_{task.id}"
            _add_entity(
                entity_id=task_ent_id,
                entity_type=EntityType.TASK,
                name=task.title,
                description=f"Task #{task.id} (Status: {task.status.value}, Priority: {task.priority.value})",
                doc_id=f"task_{task.id}",
            )
            if task.owner:
                person_id = f"person_{task.owner.lower().replace(' ', '_')}"
                _add_entity(
                    entity_id=person_id,
                    entity_type=EntityType.PERSON,
                    name=task.owner,
                    doc_id=f"task_{task.id}",
                )

        # 3. Extract Vendors & Milestones / Deliverables from Text Content
        for doc in documents:
            text = doc.text
            # Vendor detection
            for pattern in _VENDOR_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    norm_name = match.strip()
                    vendor_id = f"vendor_{norm_name.lower().replace(' ', '_').replace('.', '')}"
                    _add_entity(
                        entity_id=vendor_id,
                        entity_type=EntityType.VENDOR,
                        name=norm_name,
                        description=f"Third-party vendor referenced in {doc.source.value}",
                        doc_id=doc.id,
                    )

            # Milestone / Deliverable detection
            if "go-live" in text.lower() or "cutover" in text.lower():
                _add_entity(
                    entity_id="milestone_golive",
                    entity_type=EntityType.MILESTONE,
                    name="Project Go-Live",
                    description="Planned project cutover and go-live milestone",
                    doc_id=doc.id,
                )

            if "uat" in text.lower() or "user acceptance" in text.lower():
                _add_entity(
                    entity_id="milestone_uat",
                    entity_type=EntityType.MILESTONE,
                    name="User Acceptance Testing (UAT)",
                    description="User acceptance testing phase milestone",
                    doc_id=doc.id,
                )

            if "gdpr" in text.lower() or "compliance" in text.lower():
                _add_entity(
                    entity_id="deliverable_gdpr_cert",
                    entity_type=EntityType.DELIVERABLE,
                    name="GDPR Compliance Certification",
                    description="Regulatory compliance certification deliverable",
                    doc_id=doc.id,
                )

            if "gl_accounts" in text.lower() or "sap" in text.lower():
                _add_entity(
                    entity_id="app_sap_s4hana",
                    entity_type=EntityType.APPLICATION,
                    name="SAP S/4HANA ERP System",
                    description="Target enterprise resource planning system",
                    doc_id=doc.id,
                )

        result = list(entities_map.values())
        _log.info("Extracted %d unique entities for project_id=%s", len(result), snapshot.project.project_id)
        return result
