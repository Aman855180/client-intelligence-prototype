"""
Pydantic models for the Client Intelligence Report.

These models are the enforcement layer for hallucination control:
the LLM's raw JSON output is parsed against these models, and any
response that does not conform (missing evidence, out-of-range
confidence, invalid classification tag, etc.) is rejected rather
than silently passed through to the client.
"""

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------
# Request / response envelope models
# ---------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    conversation: str = Field(..., min_length=1, description="Raw coach-client conversation transcript")


# ---------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------

class Classification(str, Enum):
    confirmed_fact = "confirmed_fact"
    client_reported = "client_reported"
    ai_inference = "ai_inference"
    missing_information = "missing_information"
    conflicting_reports = "conflicting_reports"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ActionSource(str, Enum):
    coach = "coach"
    client = "client"
    accountability_coach = "accountability_coach"


class ActionStatus(str, Enum):
    open = "open"
    completed = "completed"
    carried_over = "carried_over"


class EvidenceItem(BaseModel):
    day: str
    speaker: Optional[str] = None
    quote: str = Field(..., max_length=300)


class GradedField(BaseModel):
    """
    The core reusable unit: every important finding in the report is
    a GradedField. Enforces that non-missing findings carry evidence,
    and that confidence stays in range.
    """
    value: Optional[Union[str, float, int, bool, list]] = None
    classification: Classification
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)

    @field_validator("evidence")
    @classmethod
    def evidence_required_unless_missing(cls, v, info):
        classification = info.data.get("classification")
        if classification and classification != Classification.missing_information and len(v) == 0:
            raise ValueError(
                "evidence must not be empty unless classification is 'missing_information'"
            )
        return v


# ---------------------------------------------------------------------
# Section models
# ---------------------------------------------------------------------

class Period(BaseModel):
    start_day: str
    end_day: str
    days_covered: List[str]


class Nutrition(BaseModel):
    adherence: GradedField
    notes: GradedField


class Exercise(BaseModel):
    steps: GradedField
    activity_type: GradedField
    consistency: GradedField


class Sleep(BaseModel):
    average_hours: GradedField
    quality_notes: GradedField


class Symptoms(BaseModel):
    reported_symptoms: GradedField
    frequency_pattern: GradedField


class Engagement(BaseModel):
    level: GradedField
    responsiveness: GradedField
    missed_checkins: GradedField


class KeyBarrier(BaseModel):
    description: str
    classification: Classification
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem]


class PendingAction(BaseModel):
    description: str
    source: ActionSource
    status: ActionStatus
    classification: Classification
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem]


class RiskFlag(BaseModel):
    flag: str
    severity: Severity
    rule_triggered: str
    classification: Classification
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(..., min_length=1)


class CoachRecommendation(BaseModel):
    recommendation: str
    priority: Priority
    classification: Classification
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceItem]


class ConflictingReport(BaseModel):
    description: str
    classification: Classification
    evidence: List[EvidenceItem] = Field(..., min_length=2)


class MissingInformationItem(BaseModel):
    category: str
    note: str


# ---------------------------------------------------------------------
# Top-level report
# ---------------------------------------------------------------------

class ClientIntelligenceReport(BaseModel):
    client_id: str
    report_id: str
    period: Period

    weekly_summary: GradedField
    nutrition: Nutrition
    exercise: Exercise
    sleep: Sleep
    water: GradedField
    symptoms: Symptoms
    stress: GradedField
    engagement: Engagement

    key_barriers: List[KeyBarrier] = Field(default_factory=list)
    pending_actions: List[PendingAction] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    coach_recommendations: List[CoachRecommendation] = Field(default_factory=list)
    conflicting_reports: List[ConflictingReport] = Field(default_factory=list)
    missing_information: List[MissingInformationItem] = Field(default_factory=list)


# ---------------------------------------------------------------------
# API response envelope
# ---------------------------------------------------------------------

class AnalyzeResponse(BaseModel):
    success: bool
    data: Optional[ClientIntelligenceReport] = None
    error: Optional[str] = None
