import json
import re
import uuid
import hmac
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.config import settings
from src.crew import create_crew, run_agents_step_by_step, build_master_blueprint
from src.utils.output_file import OUTPUT_DIR, save_output
from src.utils.html_converter import markdown_to_html
from src.utils.section_parser import extract_sections_from_markdown
from src.db import (
    save_blueprint_record,
    get_blueprint_history,
    get_blueprint_by_run_id,
    delete_blueprint_by_run_id
)

router = APIRouter(prefix="/blueprints", tags=["Blueprints"])

RUN_ID_PATTERN = re.compile(r"[0-9a-f]{12}")


def verify_api_key(request: Request) -> None:
    """Shared-secret header dependency for all /blueprints routes.

    Skips the check when API_SECRET_KEY is empty (development mode).
    """
    if not settings.API_SECRET_KEY:
        return
    provided = request.headers.get("X-API-Key", "")
    if not hmac.compare_digest(provided, settings.API_SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


class BlueprintRequest(BaseModel):
    business_idea: str = Field(min_length=15, max_length=5000)
    technology_preference: str = Field(min_length=1, max_length=100)
    cloud_preference: str = Field(min_length=1, max_length=100)
    expected_daily_traffic: str = Field(min_length=1, max_length=100)
    delivery_timeline_months: int = Field(ge=1, le=36)
    data_hosting_country: str = Field(min_length=1, max_length=100)


def _validate_run_id(run_id: str) -> None:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid run_id '{run_id}'. Must be 12 lowercase hex characters.",
        )


@router.get("", status_code=200, dependencies=[Depends(verify_api_key)])
@router.get("/list", status_code=200, dependencies=[Depends(verify_api_key)])
@router.get("/history", status_code=200, dependencies=[Depends(verify_api_key)])
async def list_blueprints(request: Request):
    """List all saved blueprints and history from SQLite database."""
    history = get_blueprint_history(limit=100)
    run_ids = [item["run_id"] for item in history]

    if not run_ids:
        outputs_dir = OUTPUT_DIR
        if outputs_dir.exists():
            run_ids = [
                file.stem for file in outputs_dir.glob("*.html") if file.stem != "final_output"
            ]
            run_ids.sort(reverse=True)

    return {
        "total": len(history) if history else len(run_ids),
        "run_ids": run_ids,
        "history": history
    }


@router.post("/stream", dependencies=[Depends(verify_api_key)])
async def stream_blueprint_execution(payload: BlueprintRequest):
    run_id = str(uuid.uuid4())[:12]
    payload_dict = payload.model_dump()

    async def sse_event_stream():
        try:
            async for event_data in run_agents_step_by_step(payload_dict, run_id=run_id):
                if event_data.get("event") == "complete":
                    html_content = event_data.get("html", "")
                    md_content = event_data.get("markdown", "")

                    try:
                        save_blueprint_record(
                            run_id=run_id,
                            inputs=payload_dict,
                            markdown_content=md_content,
                            html_content=html_content,
                            status="completed"
                        )
                    except Exception as db_err:
                        print(f"Database save warning: {db_err}")

                    save_output(f"{run_id}.html", html_content)
                    save_output(f"{run_id}.md", md_content)

                    event_data["file_saved"] = f"outputs/{run_id}.html"

                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            err_event = {
                "event": "error",
                "run_id": run_id,
                "error": str(e),
                "message": f"Execution failed: {str(e)}"
            }
            yield f"data: {json.dumps(err_event)}\n\n"

    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("", status_code=201, dependencies=[Depends(verify_api_key)])
@router.post("/generate", status_code=201, dependencies=[Depends(verify_api_key)])
async def create_blueprint(payload: BlueprintRequest):
    run_id = str(uuid.uuid4())[:12]
    payload_dict = payload.model_dump()

    try:
        crew = create_crew(**payload_dict)
        result = await crew.kickoff_async()

        if hasattr(result, "tasks_output") and len(result.tasks_output) >= 4:
            ba_out = result.tasks_output[0].raw
            sa_out = result.tasks_output[1].raw
            ta_out = result.tasks_output[2].raw
            dp_out = result.tasks_output[3].raw
            rw_out = result.tasks_output[4].raw if len(result.tasks_output) > 4 else ""
            final_output = build_master_blueprint(
                inputs=payload_dict,
                ba_output=ba_out,
                sa_output=sa_out,
                ta_output=ta_out,
                dp_output=dp_out,
                rw_output=rw_out,
                run_id=run_id
            )
        else:
            final_output = result.raw if hasattr(result, "raw") else str(result)

        html_content = markdown_to_html(final_output, title=f"MindMesh Blueprint - {run_id}")

        save_blueprint_record(
            run_id=run_id,
            inputs=payload_dict,
            markdown_content=final_output,
            html_content=html_content,
            status="completed"
        )

        save_output(f"{run_id}.html", html_content)
        save_output(f"{run_id}.md", final_output)
        save_output("final_output.html", html_content)
        save_output("final_output.md", final_output)

        return {
            "run_id": run_id,
            "status": "completed",
            "file_saved": f"outputs/{run_id}.html",
            "markdown": final_output,
            "result": html_content
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Blueprint generation failed: {str(e)}"
        )


@router.get("/{run_id}", status_code=200, dependencies=[Depends(verify_api_key)])
async def get_blueprint(run_id: str):
    _validate_run_id(run_id)

    db_record = get_blueprint_by_run_id(run_id)
    if db_record:
        md_content = db_record.get("markdown_content", "")
        html_content = db_record.get("html_content", "")
        sections = extract_sections_from_markdown(md_content)
        return {
            "run_id": run_id,
            "status": db_record.get("status", "completed"),
            "result": html_content,
            "markdown": md_content,
            "html": html_content,
            "sections": sections,
            "created_at": db_record.get("created_at", ""),
            "business_idea": db_record.get("business_idea", ""),
            "technology_preference": db_record.get("technology_preference", ""),
            "cloud_preference": db_record.get("cloud_preference", "")
        }

    outputs_dir = OUTPUT_DIR
    html_file = outputs_dir / f"{run_id}.html"
    md_file = outputs_dir / f"{run_id}.md"

    if not html_file.exists() and not md_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Blueprint output for run_id '{run_id}' not found."
        )

    html_content = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    md_content = md_file.read_text(encoding="utf-8") if md_file.exists() else ""
    sections = extract_sections_from_markdown(md_content)

    return {
        "run_id": run_id,
        "status": "completed",
        "result": html_content,
        "markdown": md_content,
        "html": html_content,
        "sections": sections
    }


@router.delete("/{run_id}", status_code=200, dependencies=[Depends(verify_api_key)])
async def delete_blueprint(run_id: str):
    _validate_run_id(run_id)

    if run_id == "final_output":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the global fallback 'final_output'.",
        )

    db_deleted = delete_blueprint_by_run_id(run_id)

    outputs_dir = OUTPUT_DIR
    file_deleted = False
    for ext in [".html", ".md"]:
        fpath = outputs_dir / f"{run_id}{ext}"
        if fpath.exists():
            fpath.unlink()
            file_deleted = True

    if not db_deleted and not file_deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Blueprint output for run_id '{run_id}' not found.",
        )

    return {
        "run_id": run_id,
        "status": "deleted",
        "message": f"Successfully deleted blueprint {run_id} from SQLite and storage."
    }
