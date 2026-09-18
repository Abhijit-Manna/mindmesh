from crewai import Crew, Process

from backend.src.agents.technology_advisor.task import (
    create_technology_advisor_task,
)


def main():

    ba_output = """
    Business Analyst Summary:

    MVP includes user registration, restaurant browsing,
    menu viewing, cart, ordering, payment and order tracking.

    Requirements include security, scalability and reliability.
    Expected traffic: 20,000 users/day.
    Timeline: 6 months.
    Data hosting: India.
    """

    sa_output = """
    Solution Architect Summary:

    The system should contain:
    - Customer interface
    - Restaurant management
    - Delivery management
    - Admin management
    - Authentication
    - Order management
    - Payment integration
    - Notification system
    - Data storage
    - Monitoring

    The architecture should support 20,000 users/day
    and the 6-month MVP timeline.
    """

    task = create_technology_advisor_task(
        business_analyst_output=ba_output,
        solution_architect_output=sa_output,
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

    print("\n===== TECHNOLOGY ADVISOR OUTPUT =====\n")
    print(result)


if __name__ == "__main__":
    main()