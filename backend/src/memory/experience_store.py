from typing import List, Optional
from datetime import datetime

from src.db import get_db_connection
from src.memory.models import Experience


def save_experience(experience: Experience) -> int:
    """
    Save a single experience to the SQLite database.

    Returns:
        The database ID of the newly stored experience.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        created_at = experience.created_at or datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT INTO experiences (
                run_id,
                agent_name,
                experience_type,
                business_idea,
                technology_preference,
                cloud_preference,
                expected_daily_traffic,
                delivery_timeline_months,
                data_hosting_country,
                decision,
                reason,
                evaluator_score,
                evaluator_feedback,
                reusable_lesson,
                successful,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                experience.run_id,
                experience.agent_name,
                experience.experience_type,
                experience.business_idea,
                experience.technology_preference,
                experience.cloud_preference,
                experience.expected_daily_traffic,
                experience.delivery_timeline_months,
                experience.data_hosting_country,
                experience.decision,
                experience.reason,
                experience.evaluator_score,
                experience.evaluator_feedback,
                experience.reusable_lesson,
                1 if experience.successful else 0,
                created_at,
            ),
        )

        conn.commit()

        return cursor.lastrowid


def get_experiences(
    agent_name: Optional[str] = None,
    experience_type: Optional[str] = None,
    cloud_preference: Optional[str] = None,
    limit: int = 10,
) -> List[Experience]:
    """
    Retrieve stored experiences using simple structured filters.

    This is intentionally simple for the first version.
    We can add semantic/vector retrieval later.
    """

    query = """
        SELECT
            run_id,
            agent_name,
            experience_type,
            business_idea,
            technology_preference,
            cloud_preference,
            expected_daily_traffic,
            delivery_timeline_months,
            data_hosting_country,
            decision,
            reason,
            evaluator_score,
            evaluator_feedback,
            reusable_lesson,
            successful,
            created_at
        FROM experiences
        WHERE 1 = 1
    """

    params = []

    if agent_name:
        query += " AND agent_name = ?"
        params.append(agent_name)

    if experience_type:
        query += " AND experience_type = ?"
        params.append(experience_type)

    

    query += """
        ORDER BY
            evaluator_score DESC,
            created_at DESC
        LIMIT ?
    """

    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [
        Experience(
            run_id=row["run_id"],
            agent_name=row["agent_name"],
            experience_type=row["experience_type"],
            business_idea=row["business_idea"],
            technology_preference=row["technology_preference"],
            cloud_preference=row["cloud_preference"],
            expected_daily_traffic=row["expected_daily_traffic"],
            delivery_timeline_months=row["delivery_timeline_months"],
            data_hosting_country=row["data_hosting_country"],
            decision=row["decision"],
            reason=row["reason"],
            evaluator_score=row["evaluator_score"],
            evaluator_feedback=row["evaluator_feedback"],
            reusable_lesson=row["reusable_lesson"],
            successful=bool(row["successful"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]