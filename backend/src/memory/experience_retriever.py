from typing import List, Optional

from src.memory.models import Experience
from src.memory.experience_store import get_experiences


def retrieve_experiences(
    agent_name: str,
    cloud_preference: Optional[str] = None,
    technology_preference: Optional[str] = None,
    expected_daily_traffic: Optional[str] = None,
    delivery_timeline_months: Optional[int] = None,
    data_hosting_country: Optional[str] = None,
    limit: int = 3,
) -> List[Experience]:
    """
    Retrieve relevant past experiences for a specific agent.

    The first version uses simple structured matching.
    More advanced semantic/vector retrieval can be added later.
    """

    experiences = get_experiences(
        agent_name=agent_name,
        cloud_preference=cloud_preference,
        limit=limit * 3,
    )

    if not experiences:
        return []

    scored_experiences = []

    for experience in experiences:
        score = 0

        # Cloud preference match
        if cloud_preference and experience.cloud_preference:
            stored_cloud = experience.cloud_preference.lower()
            requested_cloud = cloud_preference.lower()

            if stored_cloud == requested_cloud:
                score += 3
            elif stored_cloud == "no preference":
                score += 1

        # Technology preference match
        if (
            technology_preference
            and experience.technology_preference
            and technology_preference.lower()
            in experience.technology_preference.lower()
        ):
            score += 2

        # Data hosting country match
        if (
            data_hosting_country
            and experience.data_hosting_country
            and data_hosting_country.lower()
            == experience.data_hosting_country.lower()
        ):
            score += 2

        # Delivery timeline similarity
        if (
            delivery_timeline_months is not None
            and experience.delivery_timeline_months is not None
        ):
            timeline_difference = abs(
                delivery_timeline_months
                - experience.delivery_timeline_months
            )

            if timeline_difference == 0:
                score += 2
            elif timeline_difference <= 2:
                score += 1

        # Traffic similarity
        if (
            expected_daily_traffic
            and experience.expected_daily_traffic
            and expected_daily_traffic.lower()
            == experience.expected_daily_traffic.lower()
        ):
            score += 2

        # Prefer successful experiences with strong evaluator scores.
        if experience.successful:
            score += 3
        else:
            score -= 1

        if experience.evaluator_score is not None:
            score += experience.evaluator_score

        scored_experiences.append((score, experience))

    scored_experiences.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        experience
        for _, experience in scored_experiences[:limit]
    ]


def format_experiences_for_prompt(
    experiences: List[Experience],
) -> str:
    """
    Convert retrieved experiences into a compact prompt section.

    Agents should treat these as previous lessons, not absolute rules.
    """

    if not experiences:
        return "No relevant previous experiences were found."

    sections = []

    for index, experience in enumerate(experiences, start=1):
        section = f"""
Previous Experience {index}
Agent: {experience.agent_name}
Type: {experience.experience_type}

Memory Guidance:
{"Use this as a successful pattern." if experience.successful else "Use this as a warning; avoid repeating this failed approach."}

Decision:
{experience.decision or "Not specified"}

Reason:
{experience.reason or "Not specified"}

Reusable Lesson:
{(experience.reusable_lesson or "Not specified")[:2000]}

Evaluator Score:
{experience.evaluator_score if experience.evaluator_score is not None else "Not available"}

Evaluator Feedback:
{experience.evaluator_feedback or "Not available"}
""".strip()

        sections.append(section)

    return "\n\n".join(sections)