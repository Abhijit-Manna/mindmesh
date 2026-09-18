from crewai import Crew, Process

from backend.src.agents.delivery_planner.task import (
    create_delivery_planner_task,
)


def main():

    ba_output = """
    Business Analyst Summary:

    MVP:
    - User registration
    - Restaurant browsing
    - Menu management
    - Cart
    - Order placement
    - Payment
    - Order tracking
    - Basic admin management

    Constraints:
    - 20,000 users/day
    - 6 month timeline
    - Data hosted in India
    """

    sa_output = """
    Solution Architect Summary:

    Major components:
    - Frontend
    - Backend/API
    - Authentication
    - Order management
    - Payment integration
    - Restaurant management
    - Delivery management
    - Database
    - Notifications
    - Monitoring

    Architecture must support scalability,
    security and reliability.
    """

    ta_output = """
    Technology Advisor Summary:

    Recommended technology categories:

    Backend:
    Python-based backend

    Frontend:
    Modern web frontend

    Database:
    Relational database

    Authentication:
    Token-based authentication

    Infrastructure:
    AWS-based deployment

    Testing:
    Automated unit and integration testing

    Monitoring:
    Application monitoring and centralized logging
    """

    task = create_delivery_planner_task(
        business_analyst_output=ba_output,
        solution_architect_output=sa_output,
        technology_advisor_output=ta_output,
        delivery_timeline_months=6,
    )

    crew = Crew(
        agents=[task.agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    print("\n===== DELIVERY PLANNER OUTPUT =====\n")
    print(result)


if __name__ == "__main__":
    main()