import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.crew import create_crew, run_agents_step_by_step, build_master_blueprint
from src.utils.output_file import save_output
from src.utils.html_converter import markdown_to_html
from src.db import (
    save_blueprint_record,
    get_blueprint_history,
    get_blueprint_by_run_id,
    delete_blueprint_by_run_id
)

router = APIRouter(prefix="/blueprints", tags=["Blueprints"])


class BlueprintRequest(BaseModel):
    business_idea: str
    technology_preference: str 
    cloud_preference: str 
    expected_daily_traffic: str 
    delivery_timeline_months: int
    data_hosting_country: str 


@router.get("", status_code=200)
@router.get("/list", status_code=200)
@router.get("/history", status_code=200)
async def list_blueprints():
    """List all saved blueprints and history from SQLite database."""
    history = get_blueprint_history(limit=100)
    run_ids = [item["run_id"] for item in history]

    # Fallback to filesystem if DB was empty but files exist
    if not run_ids:
        outputs_dir = Path("outputs")
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


@router.post("/stream")
async def stream_blueprint_execution(payload: BlueprintRequest):
    """
    Stream agent execution step-by-step using Server-Sent Events (SSE) and save to SQLite.
    """
    run_id = str(uuid.uuid4())[:12]
    payload_dict = payload.model_dump()

    async def sse_event_stream():
        try:
            async for event_data in run_agents_step_by_step(payload_dict, run_id=run_id):
                # When complete event is produced, persist to SQLite DB and files
                if event_data.get("event") == "complete":
                    html_content = event_data.get("html", "")
                    md_content = event_data.get("markdown", "")
                    
                    # Persist to SQLite DB
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

                    # Also save fallback file outputs
                    save_output(f"{run_id}.html", html_content)
                    save_output(f"{run_id}.md", md_content)
                    save_output("final_output.html", html_content)
                    save_output("final_output.md", md_content)
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


@router.post("", status_code=201)
@router.post("/generate", status_code=201)
async def create_blueprint(payload: BlueprintRequest):
    """
    Synchronous / standard generation endpoint saving to SQLite DB.
    """
    run_id = str(uuid.uuid4())[:12]
    payload_dict = payload.model_dump()

    try:
        crew = create_crew(**payload_dict)
        result = await crew.kickoff_async()
        
        if hasattr(result, "tasks_output") and len(result.tasks_output) >= 5:
            ba_out = result.tasks_output[0].raw
            sa_out = result.tasks_output[1].raw
            ta_out = result.tasks_output[2].raw
            do_out = result.tasks_output[3].raw
            dp_out = result.tasks_output[4].raw
            rw_out = result.tasks_output[5].raw if len(result.tasks_output) > 5 else ""
            final_output = build_master_blueprint(
                inputs=payload_dict,
                ba_output=ba_out,
                sa_output=sa_out,
                ta_output=ta_out,
                do_output=do_out,
                dp_output=dp_out,
                rw_output=rw_out,
                run_id=run_id
            )
        else:
            final_output = result.raw if hasattr(result, "raw") else str(result)
        
        html_content = markdown_to_html(final_output, title=f"MindMesh Blueprint - {run_id}")
        
        # Save to SQLite Database
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


@router.get("/{run_id}", status_code=200)
async def get_blueprint(run_id: str):
    """Retrieve saved blueprint output from SQLite database or fallback files."""
    # First attempt from SQLite DB
    db_record = get_blueprint_by_run_id(run_id)
    if db_record:
        return {
            "run_id": run_id,
            "status": db_record.get("status", "completed"),
            "result": db_record.get("html_content", ""),
            "markdown": db_record.get("markdown_content", ""),
            "html": db_record.get("html_content", ""),
            "created_at": db_record.get("created_at", ""),
            "business_idea": db_record.get("business_idea", ""),
            "technology_preference": db_record.get("technology_preference", ""),
            "cloud_preference": db_record.get("cloud_preference", "")
        }

    # Fallback to filesystem
    outputs_dir = Path("outputs")
    html_file = outputs_dir / f"{run_id}.html"
    md_file = outputs_dir / f"{run_id}.md"

    if not html_file.exists() and not md_file.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Blueprint output for run_id '{run_id}' not found."
        )

    html_content = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    md_content = md_file.read_text(encoding="utf-8") if md_file.exists() else ""

    return {
        "run_id": run_id,
        "status": "completed",
        "result": html_content,
        "markdown": md_content,
        "html": html_content
    }


@router.delete("/{run_id}", status_code=200)
async def delete_blueprint(run_id: str):
    """Delete a specific blueprint from SQLite database and outputs."""
    if run_id == "final_output":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the global fallback 'final_output'.",
        )

    db_deleted = delete_blueprint_by_run_id(run_id)

    outputs_dir = Path("outputs")
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