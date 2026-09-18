from crewai import Crew, Process

from backend.src.agents.business_analyst.task import (
    create_business_analyst_task,
)


def main():
    task = create_business_analyst_task(
        business_idea="Online food delivery platform",
        technology_preference="open-source",
        cloud_preference="AWS",
        expected_daily_traffic="20,000 users/day",
        delivery_timeline_months=6,
        data_hosting_country="India",
    )

    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    print("\n===== BUSINESS ANALYST OUTPUT =====\n")
    print(result)


if __name__ == "__main__":
    main()