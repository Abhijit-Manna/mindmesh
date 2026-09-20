from typing import Any, Dict, Optional

from src.memory.models import Experience


def extract_experience(
    run_id: str,
    agent_name: str,
    agent_output: str,
    user_inputs: Dict[str, Any],
    evaluation: Dict[str, Any],
) -> Optional[Experience]:
    """
    Convert an evaluated agent result into a reusable experience.

    This first implementation is intentionally deterministic and does
    not make another LLM call.

    The goal is to capture:
    - the agent involved
    - the project constraints
    - evaluator result
    - evaluator feedback
    - the agent output as the reusable lesson

    A more sophisticated extraction strategy can be added later.
    """

    if not agent_output:
        return None

    score = evaluation.get("score")
    passed = evaluation.get("passed", False)

    summary = evaluation.get("summary", "")
    critique = evaluation.get("critique", "")
    remediation = evaluation.get("remediation_guidance", "")

    # Determine the type of experience based on the evaluation.
    if passed:
        experience_type = "successful_pattern"
    else:
        experience_type = "failed_attempt"

    # Build a useful reason from the evaluator's feedback.
    feedback_parts = []

    if summary:
        feedback_parts.append(f"Summary: {summary}")

    if critique:
        feedback_parts.append(f"Critique: {critique}")

    if remediation:
        feedback_parts.append(
            f"Remediation: {remediation}"
        )

    evaluator_feedback = "\n".join(feedback_parts)

    # Keep the reusable lesson compact enough that it can safely
    # be injected into future agent prompts.
    reusable_lesson = agent_output

    return Experience(
        run_id=run_id,
        agent_name=agent_name,
        experience_type=experience_type,

        business_idea=user_inputs.get("business_idea"),
        technology_preference=user_inputs.get(
            "technology_preference"
        ),
        cloud_preference=user_inputs.get(
            "cloud_preference"
        ),
        expected_daily_traffic=user_inputs.get(
            "expected_daily_traffic"
        ),
        delivery_timeline_months=_safe_int(
            user_inputs.get("delivery_timeline_months")
        ),
        data_hosting_country=user_inputs.get(
            "data_hosting_country"
        ),

        decision=None,
        reason=evaluator_feedback,

        evaluator_score=score,
        evaluator_feedback=evaluator_feedback,

        reusable_lesson=reusable_lesson,

        successful=bool(passed),
    )


def _safe_int(value: Any) -> Optional[int]:
    """
    Safely convert a value to an integer.

    Returns None if conversion is not possible.
    """
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None