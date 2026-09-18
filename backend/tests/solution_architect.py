from crewai import Crew, Process

from backend.src.agents.solution_architect.task import (
    create_solution_architect_task,
)


def main():

    ba_output = """
    Business Analyst Summary:

    Users:
    - Customers
    - Restaurants
    - Delivery Drivers
    - Administrators

    MVP:
    - User registration
    - Restaurant browsing
    - Menu viewing
    - Cart
    - Order placement
    - Payment
    - Order tracking

    Constraints:
    - Open-source preference
    - AWS cloud
    - 20,000 users/day
    - 6 month delivery timeline
    - Data hosted in India
    """

    task = create_solution_architect_task(
        business_analyst_output=ba_output,
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

    print("\n===== SOLUTION ARCHITECT OUTPUT =====\n")
    print(result)


if __name__ == "__main__":
    main()