from dataclasses import dataclass
from typing import Optional


@dataclass
class Experience:
    """
    A reusable lesson learned from a previous MindMesh agent run.

    Experiences are stored after an agent produces an evaluated result
    and can later be retrieved to give future agents relevant context.
    """

    run_id: str
    agent_name: str
    experience_type: str

    business_idea: Optional[str] = None
    technology_preference: Optional[str] = None
    cloud_preference: Optional[str] = None
    expected_daily_traffic: Optional[str] = None
    delivery_timeline_months: Optional[int] = None
    data_hosting_country: Optional[str] = None

    decision: Optional[str] = None
    reason: Optional[str] = None

    evaluator_score: Optional[float] = None
    evaluator_feedback: Optional[str] = None

    reusable_lesson: Optional[str] = None

    successful: bool = True

    created_at: Optional[str] = None