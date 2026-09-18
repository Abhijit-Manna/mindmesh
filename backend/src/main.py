from backend.src.crew import create_crew
from backend.src.utils.output_file import save_output

def main():
    crew = create_crew(
        business_idea="An online platform for booking home healthcare services",
        technology_preference="Python",
        cloud_preference="AWS",
        expected_daily_traffic="10,000 users per day",
        delivery_timeline_months=3,
        data_hosting_country="India",
    )

    result = crew.kickoff()

    save_output("final_output.md", result)

    print(result)


if __name__ == "__main__":
    main()