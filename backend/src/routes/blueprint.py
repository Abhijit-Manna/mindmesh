from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid
from src.crew import create_crew
from src.utils.output_file import save_output

router = APIRouter(prefix="/api/v1/blueprints", tags=["Blueprints"])

class BlueprintRequest(BaseModel):
    business_idea: str
    technology_preference: str 
    cloud_preference: str 
    expected_daily_traffic: str 
    delivery_timeline_months: int
    data_hosting_country: str 

#class RegenerateRequest(BaseModel):
   # target_agent: str
  #  user_input: str | None = None

@router.get("", status_code=200)
async def list_blueprints():
    """List all available run_ids generated from previous executions."""
    outputs_dir = Path("outputs")

    if not outputs_dir.exists():
        return {"total": 0, "run_ids": []}

    # Gather all file stems except the fallback 'final_output'
    run_ids = [
        file.stem for file in outputs_dir.glob("*.md") if file.stem != "final_output"
    ]

    return {"total": len(run_ids), "run_ids": run_ids}

@router.post("", status_code=201)
async def create_blueprint(payload: BlueprintRequest):
    run_id = str(uuid.uuid4())
    try:
        crew = create_crew(
            business_idea=payload.business_idea,
            technology_preference=payload.technology_preference,
            cloud_preference=payload.cloud_preference,
            expected_daily_traffic=payload.expected_daily_traffic,
            delivery_timeline_months=payload.delivery_timeline_months,
            data_hosting_country=payload.data_hosting_country,
        )

        result = await crew.kickoff_async()
        markdown_content = result.raw if hasattr(result, "raw") else str(result)
        filename=f"{run_id}.md"
        save_output(filename, markdown_content)

        save_output("final_output.md", markdown_content)

        return {"run_id": run_id, "status": "completed", "file_saved": f"output/{filename}" ,"result": str(result)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Blueprint generation failed: {str(e)}"
        )


@router.get("/{run_id}", status_code=200)
async def get_blueprint(run_id: str):
    file_path = Path("outputs") / f"{run_id}.md"

    # Check if the output file actually exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Blueprint output for run_id '{run_id}' not found."
        )

    # Read and return the saved markdown content
    content = file_path.read_text(encoding="utf-8")

    return {
        "run_id": run_id,
        "status": "completed",
        "result": content
    }


@router.delete("/{run_id}", status_code=200)
async def delete_blueprint(run_id: str):
    """Delete a specific blueprint output file by run_id."""
    if run_id == "final_output":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the global fallback 'final_output.md'.",
        )

    file_path = Path("outputs") / f"{run_id}.md"

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Blueprint output for run_id '{run_id}' not found.",
        )

    file_path.unlink()

    return {"run_id": run_id, "status": "deleted", "message": f"Successfully deleted outputs/{run_id}.md"}


#@router.post("/{run_id}/regenerate", status_code=201)
#async def regenerate_blueprint(run_id: str, payload: RegenerateRequest):
 #   new_run_id = str(uuid.uuid4())
    # Regenerate target_agent and downstream agents, returning new child run
  #  return {"parent_run_id": run_id, "child_run_id": new_run_id, "status": "started"}