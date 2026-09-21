import asyncio
import json
import re
from typing import Any, Dict
from crewai import Crew

from src.agents.evaluator.task import create_evaluator_task


def parse_evaluation_json(eval_raw: str) -> Dict[str, Any]:
    """
    Parse JSON evaluation output from the evaluator agent.
    Safely extracts JSON even if enclosed in markdown code fences or surrounded by commentary.
    """
    try:
        # Match ```json { ... } ``` or ``` { ... } ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", eval_raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(1))
            return parsed if isinstance(parsed, dict) else _invalid_evaluation_result()
        # Match standalone JSON {...}
        match_raw = re.search(r"(\{.*?\})", eval_raw, re.DOTALL)
        if match_raw:
            parsed = json.loads(match_raw.group(1))
            return parsed if isinstance(parsed, dict) else _invalid_evaluation_result()
        parsed = json.loads(eval_raw)
        return parsed if isinstance(parsed, dict) else _invalid_evaluation_result()
    except (json.JSONDecodeError, TypeError, AttributeError):
        return _invalid_evaluation_result()


def _invalid_evaluation_result() -> Dict[str, Any]:
    return {
        "score": 0.0,
        "passed": False,
        "summary": "Evaluator output could not be parsed.",
        "critique": ["Evaluator returned malformed or non-object JSON output."],
        "remediation_guidance": "Return a JSON object using the required evaluation schema.",
    }


async def evaluate_agent_output(
    agent_role: str,
    agent_output: str,
    inputs: Dict[str, Any],
    threshold: float = 0.70,
    upstream_context: str = "",
) -> Dict[str, Any]:
    """
    Run the quality evaluation gate on an agent's deliverable using the Evaluator agent.
    Returns parsed evaluation score, pass/fail status, critique, and remediation notes.
    """
    eval_task = create_evaluator_task(
        agent_role=agent_role,
        agent_output=agent_output,
        user_constraints=inputs,
        threshold=threshold,
        upstream_context=upstream_context,
    )
    eval_crew = Crew(agents=[eval_task.agent], tasks=[eval_task], verbose=False)
    res = await asyncio.to_thread(eval_crew.kickoff)
    raw_text = res.raw if hasattr(res, "raw") else str(res)
    parsed = parse_evaluation_json(raw_text)

    raw_score = parsed.get("score", 0.0)
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        score = 0.0
        parsed.setdefault(
            "critique",
            [],
        )
        if isinstance(parsed["critique"], list):
            parsed["critique"].append(
                "Evaluator returned a non-numeric score; output was rejected."
            )
        parsed.setdefault(
            "remediation_guidance",
            "Return a numeric score between 0.0 and 1.0.",
        )

    score = max(0.0, min(score, 1.0))
    parsed["score"] = score
    parsed["passed"] = score >= threshold
    return parsed
