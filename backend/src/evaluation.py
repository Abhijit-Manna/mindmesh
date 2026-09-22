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
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", eval_raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(1))
            return parsed if isinstance(parsed, dict) else _invalid_evaluation_result()
        # Find first { and use raw_decode to handle nested braces correctly
        match_raw = re.search(r"\{", eval_raw)
        if match_raw:
            start = match_raw.start()
            decoder = json.JSONDecoder()
            obj, _ = decoder.raw_decode(eval_raw, idx=start)
            return obj if isinstance(obj, dict) else _invalid_evaluation_result()
        parsed = json.loads(eval_raw)
        return parsed if isinstance(parsed, dict) else _invalid_evaluation_result()
    except (json.JSONDecodeError, TypeError, AttributeError, ValueError):
        return _invalid_evaluation_result()


def _invalid_evaluation_result() -> Dict[str, Any]:
    return {
        "score": 0.0,
        "passed": False,
        "summary": "Evaluator output could not be parsed.",
        "critique": ["Evaluator returned malformed or non-object JSON output."],
        "remediation_guidance": "Return a JSON object using the required evaluation schema.",
    }


def structural_check(agent_role: str, agent_output: str) -> tuple:
    """
    Deterministic structural check before the evaluator LLM call.

    Catches clearly deficient outputs without spending an LLM call:
    - All agents: minimum length
    - Solution Architect: flowchart TD diagram present
    - Report Writer: all 14 numbered headings present;
      sections 4, 6, 9, 12 each over 800 chars

    Returns (passed: bool, reason: str).
    """
    if not agent_output or len(agent_output.strip()) < 100:
        return False, "Output is too short to be substantive"

    normalized = agent_output.strip()
    normalized_lower = normalized.lower()

    if agent_role == "solution architect":
        if "flowchart td" not in normalized_lower:
            return False, "Missing required Mermaid flowchart TD diagram"

    if agent_role == "report writer":
        for i in range(1, 15):
            if f"## {i}." not in normalized:
                return False, f"Missing required section heading: ## {i}."

        for section_num in (4, 6, 9, 12):
            pattern = re.compile(
                rf"## {section_num}\..*?(?=\n## \d+\.|\Z)",
                re.DOTALL | re.IGNORECASE,
            )
            m = pattern.search(normalized)
            if not m or len(m.group(0)) < 800:
                return False, (
                    f"Section {section_num} lacks substantive content "
                    f"(must be over 800 chars)"
                )

    return True, ""


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
    structural_passed, structural_reason = structural_check(agent_role, agent_output)
    if not structural_passed:
        return {
            "score": 0.0,
            "passed": False,
            "summary": f"Structural check failed: {structural_reason}",
            "critique": [structural_reason],
            "remediation_guidance": (
                f"Address the structural issue before resubmitting: {structural_reason}"
            ),
        }

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
    llm_passed = bool(parsed.get("passed", False))
    parsed["passed"] = llm_passed and score >= threshold
    # Detect parse failure: _invalid_evaluation_result has a unique remediation_guidance.
    parsed["parse_ok"] = (
        parsed.get("remediation_guidance")
        != "Return a JSON object using the required evaluation schema."
    )
    return parsed
