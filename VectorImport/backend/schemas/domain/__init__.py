"""
schemas/domain/__init__.py
--------------------------
Public surface of the domain schemas package.
"""

from schemas.domain.snapshot import ProjectSnapshot

from schemas.domain.project import (
    ProjectCreateSchema, ProjectUpdateSchema, ProjectSchema,
    ProjectTaskCreateSchema, ProjectTaskUpdateSchema, ProjectTaskSchema,
    StakeholderCreateSchema, StakeholderUpdateSchema, StakeholderSchema,
    ProjectStatus, TaskPriority, TaskStatus, CommunicationPreference,
)
from schemas.domain.communications import (
    EmailDocumentCreateSchema, EmailDocumentUpdateSchema, EmailDocumentSchema,
    ChatMessageCreateSchema, ChatMessageUpdateSchema, ChatMessageSchema,
    MeetingNoteCreateSchema, MeetingNoteUpdateSchema, MeetingNoteSchema,
    MeetingActionItem,
)
from schemas.domain.risks import (
    RiskEntryCreateSchema, RiskEntryUpdateSchema, RiskEntrySchema,
    RiskProbability, RiskImpact, RiskStatus,
)
from schemas.domain.reports import (
    StatusReportCreateSchema, StatusReportUpdateSchema, StatusReportSchema,
)
from schemas.domain.historical import (
    HistoricalProjectCreateSchema, HistoricalProjectUpdateSchema, HistoricalProjectSchema,
    HistoricalRisk,
)
from schemas.domain.normalized_document import NormalizedDocument, DocumentSource
from schemas.domain.knowledge_entity import KnowledgeEntity, EntityType
from schemas.domain.relationship import Relationship, RelationshipType
from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.risk_report import (
    CategorizedRisk,
    EvidenceItem,
    EvidenceReference,
    EvidencePackage,
    EvidenceTrace,
    MitigationPlan,
    ReflectionFeedback,
    RiskAssessmentReport,
)

__all__ = [
    # Canonical business objects
    "ProjectSnapshot",
    "ProjectKnowledgeBundle",
    "RiskAssessmentReport",
    "CategorizedRisk",
    "EvidenceItem",
    "EvidenceReference",
    "EvidencePackage",
    "EvidenceTrace",
    "MitigationPlan",
    "ReflectionFeedback",
    # Graph 1 pipeline outputs
    "NormalizedDocument", "DocumentSource",
    "KnowledgeEntity", "EntityType",
    "Relationship", "RelationshipType",
    # Project
    "ProjectSchema", "ProjectCreateSchema", "ProjectUpdateSchema", "ProjectStatus",
    # Task
    "ProjectTaskSchema", "ProjectTaskCreateSchema", "ProjectTaskUpdateSchema",
    "TaskPriority", "TaskStatus",
    # Stakeholder
    "StakeholderSchema", "StakeholderCreateSchema", "StakeholderUpdateSchema",
    "CommunicationPreference",
    # Communications
    "EmailDocumentSchema", "EmailDocumentCreateSchema", "EmailDocumentUpdateSchema",
    "ChatMessageSchema", "ChatMessageCreateSchema", "ChatMessageUpdateSchema",
    "MeetingNoteSchema", "MeetingNoteCreateSchema", "MeetingNoteUpdateSchema",
    "MeetingActionItem",
    # Risks
    "RiskEntrySchema", "RiskEntryCreateSchema", "RiskEntryUpdateSchema",
    "RiskProbability", "RiskImpact", "RiskStatus",
    # Reports
    "StatusReportSchema", "StatusReportCreateSchema", "StatusReportUpdateSchema",
    # Historical
    "HistoricalProjectSchema", "HistoricalProjectCreateSchema", "HistoricalProjectUpdateSchema",
    "HistoricalRisk",
]
