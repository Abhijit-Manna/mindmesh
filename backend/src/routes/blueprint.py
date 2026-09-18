from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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

@router.post("", status_code=201)
async def create_blueprint(payload: BlueprintRequest):
    run_id = str(uuid.uuid4())

    crew = create_crew(
        business_idea=payload.business_idea,
        technology_preference=payload.technology_preference,
        cloud_preference=payload.cloud_preference,
        expected_daily_traffic=payload.expected_daily_traffic,
        delivery_timeline_months=payload.delivery_timeline_months,
        data_hosting_country=payload.data_hosting_country,
    )

    result = await crew.kickoff_async()
    save_output(f"{run_id}.md", result)

    return {"run_id": run_id, "status": "completed", "result": str(result)}

@router.get("/{run_id}", status_code=200)
async def get_blueprint(run_id: str):
    # Retrieve completed output by run_id without re-running agents
    return {"run_id": run_id, "data": "blueprint_result"}

#@router.post("/{run_id}/regenerate", status_code=201)
#async def regenerate_blueprint(run_id: str, payload: RegenerateRequest):
 #   new_run_id = str(uuid.uuid4())
    # Regenerate target_agent and downstream agents, returning new child run
  #  return {"parent_run_id": run_id, "child_run_id": new_run_id, "status": "started"}