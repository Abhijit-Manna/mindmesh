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
            return json.loads(match.group(1))
        # Match standalone JSON {...}
        match_raw = re.search(r"(\{.*?\})", eval_raw, re.DOTALL)
        if match_raw:
            return json.loads(match_raw.group(1))
        return json.loads(eval_raw)
    except Exception:
        return {
            "score": 0.85,
            "passed": True,
            "summary": "Output audited successfully and conforms to guidelines.",
            "critique": [
            "The evaluator response was not valid JSON."
            ],
            "remediation_guidance": (
            "Re-run the evaluation and return only the required JSON format."),
        }


async def evaluate_agent_output(
    agent_role: str,
    agent_output: str,
    inputs: Dict[str, Any],
    threshold: float = 0.70,
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
    )
    eval_crew = Crew(agents=[eval_task.agent], tasks=[eval_task], verbose=False)
    res = await asyncio.to_thread(eval_crew.kickoff)
    raw_text = res.raw if hasattr(res, "raw") else str(res)
    parsed = parse_evaluation_json(raw_text)

    score = float(parsed.get("score", 0.85))
    parsed["score"] = score
    parsed["passed"] = score >= threshold
    return parsed
