from fastapi import FastAPI

from src.config import settings
from src.crew import create_crew
from src.routes import blueprint, health
from src.routes.blueprint import BlueprintRequest
from src.utils.output_file import save_output

app = FastAPI(title=settings.APP_NAME)

app.include_router(health.router)
app.include_router(blueprint.router, prefix="/api/v1")

def main():
    # Pass inputs directly to instantiate the BaseModel
    request_data = BlueprintRequest(
        business_idea="An online platform for booking home healthcare services",
        technology_preference="Python",
        cloud_preference="AWS",
        expected_daily_traffic="10,000 users per day",
        delivery_timeline_months=3,
        data_hosting_country="India",
    )
    crew = create_crew(**request_data.model_dump())

    result = crew.kickoff()
    save_output("final_output.md", result)
    print(result)


if __name__ == "__main__":
    main()