from typing import Dict

from src.blueprint_builder import _extract_numbered_section


def extract_sections_from_markdown(md_text: str) -> Dict[str, str]:
    """
    Extracts per-agent sections from the synthesized master blueprint.

    Maps each tab to the canonical numbered heading produced by
    build_master_blueprint:
      business_analyst      -> ## 2. Business / MVP Scope and Priorities
      solution_architect    -> ## 9. High-Level Solution Architecture
      technology_advisor    -> ## 3. Recommended Technology Stack
      delivery_planner      -> ## 4/5/6 combined (Workstreams, Team, Timeline)
    """
    if not md_text:
        return {
            "business_analyst": "",
            "solution_architect": "",
            "technology_advisor": "",
            "delivery_planner": "",
        }

    ba = _extract_numbered_section(md_text, 2)
    sa = _extract_numbered_section(md_text, 9)
    ta = _extract_numbered_section(md_text, 3)

    dp_parts = [
        _extract_numbered_section(md_text, n)
        for n in (4, 5, 6)
    ]
    dp = "\n\n---\n\n".join(p for p in dp_parts if p and p.strip())

    return {
        "business_analyst": ba,
        "solution_architect": sa,
        "technology_advisor": ta,
        "delivery_planner": dp,
    }
