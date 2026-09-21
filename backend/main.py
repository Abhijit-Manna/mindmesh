from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.crew import create_crew
from src.routes import blueprint, health
from src.routes.blueprint import BlueprintRequest
from src.utils.output_file import save_output
from src.utils.html_converter import markdown_to_html

app = FastAPI(
    title=settings.APP_NAME,
    description="MindMesh Multi-Agent Solution Architecture Engine API",
    version="1.0.0"
)

# Enable CORS for frontend clients (Streamlit on port 8501, Vite, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registrations
app.include_router(health.router)
app.include_router(blueprint.router, prefix="/api/v1")


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

        print("[3/3] Execution completed. Converting output to HTML...")
        html_output = markdown_to_html(str(result))
        save_output("final_output.html", html_output)
        print("Success! Output saved to outputs/final_output.html")

    except Exception as e:
        print(f"\nExecution failed with error: {e}")


if __name__ == "__main__":
    main()