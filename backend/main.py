from fastapi import FastAPI

from src.config import settings
from src.crew import create_crew
from src.routes import blueprint, health
from src.routes.blueprint import BlueprintRequest
from src.utils.output_file import save_output

app = FastAPI(title=settings.APP_NAME)

app.include_router(health.router)
app.include_router(blueprint.router, prefix="/api/v1")

# -------------------------------------------------------------------------
    # LOCAL CLI TEST RUNNER
    # This block is ONLY executed when running `python main.py` directly.
    # It is ignored when launching the FastAPI server (`fastapi dev main.py`).
    # Use this to quickly verify CrewAI agent workflows without Uvicorn.
    # -------------------------------------------------------------------------

def main():
    print("[1/3] Preparing test payload...")
    request_data = BlueprintRequest(
        business_idea="An online platform for booking home healthcare services",
        technology_preference="Python",
        cloud_preference="AWS",
        expected_daily_traffic="10,000 users per day",
        delivery_timeline_months=3,
        data_hosting_country="India",
    )

    try:
        print("[2/3] Executing CrewAI workflow (this may take 1-2 minutes)...")
        crew = create_crew(**request_data.model_dump())
        result = crew.kickoff()

        print("[3/3] Execution completed. Writing output file...")
        save_output("final_output.md", result)
        print("Success! Output saved to outputs/final_output.md")

    except Exception as e:
        print(f"\nExecution failed with error: {e}")


if __name__ == "__main__":
    main()