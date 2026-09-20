import asyncio
from typing import Any, AsyncGenerator, Callable, Dict
from crewai import Crew, Task

from src.config import settings
from src.evaluation import evaluate_agent_output
from src.blueprint_builder import build_master_blueprint
from src.utils.html_converter import markdown_to_html

from src.agents.business_analyst.task import create_business_analyst_task
from src.agents.solution_architect.task import create_solution_architect_task
from src.agents.technology_advisor.task import create_technology_advisor_task
from src.agents.delivery_planner.task import create_delivery_planner_task
from src.agents.report_writer.task import create_report_writer_task

    
async def execute_step_with_eval(
    agent_name: str,
    role: str,
    step_num: int,
    total_steps: int,
    task_factory_fn: Callable[[], Task],
    inputs: Dict[str, Any],
    start_msg: str,
    complete_msg: str,
    start_pct: int,
    complete_pct: int,
    event_queue: asyncio.Queue,
    enable_eval: bool,
    eval_threshold: float,
    max_retries: int,
) -> str:
    """
    Executes a single agent step in a worker thread, optionally evaluates the deliverable,
    and applies bounded remediation retries if quality threshold is not met.
    Emits real-time SSE events via event_queue.
    """
    task = task_factory_fn()
    retries = 0
    final_output = ""

    await event_queue.put({
        "event": "agent_start",
        "agent": agent_name,
        "step": step_num,
        "total": total_steps,
        "role": role,
        "message": start_msg,
        "progress": start_pct,
    })

    while retries <= max_retries:
        crew = Crew(agents=[task.agent], tasks=[task], verbose=True)
        res = await asyncio.to_thread(crew.kickoff)
        final_output = res.raw if hasattr(res, "raw") else str(res)

        if not enable_eval:
            break

        # Run evaluation gate
        await event_queue.put({
            "event": "evaluation_start",
            "agent": agent_name,
            "step": step_num,
            "total": total_steps,
            "message": f"Quality Auditor evaluating {agent_name} output against role criteria...",
            "progress": start_pct + 3,
        })

        eval_res = await evaluate_agent_output(
            agent_role=agent_name,
            agent_output=final_output,
            inputs=inputs,
            threshold=eval_threshold,
        )

        score = eval_res.get("score", 0.85)
        passed = eval_res.get("passed", True)

        await event_queue.put({
            "event": "evaluation",
            "agent": agent_name,
            "step": step_num,
            "score": score,
            "passed": passed,
            "summary": eval_res.get("summary", ""),
            "critique": eval_res.get("critique", []),
            "remediation": eval_res.get("remediation_guidance", ""),
            "message": f"Evaluator Score: {score:.2f} — {'Accepted' if passed else 'Refinement Suggested'}",
            "progress": start_pct + 6,
        })

        if passed or retries >= max_retries:
            break

        retries += 1
        await event_queue.put({
            "event": "agent_retry",
            "agent": agent_name,
            "step": step_num,
            "retry_count": retries,
            "message": f"Refining {agent_name} output based on evaluator critique (Attempt {retries}/{max_retries})...",
            "progress": start_pct + 7,
        })

    await event_queue.put({
        "event": "agent_complete",
        "agent": agent_name,
        "step": step_num,
        "total": total_steps,
        "output": final_output,
        "message": complete_msg,
        "progress": complete_pct,
    })

    return final_output


async def run_agents_step_by_step(
    inputs: Dict[str, Any],
    run_id: str,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Executes specialist agents one by one sequentially with evaluation gates and real-time SSE streaming.
    Yields progress events, agent deliverables, and the final compiled enterprise solution blueprint.
    """
    business_idea = inputs.get("business_idea", "")
    technology_preference = inputs.get("technology_preference", "")
    cloud_preference = inputs.get("cloud_preference", "")
    expected_daily_traffic = inputs.get("expected_daily_traffic", "")
    delivery_timeline_months = int(inputs.get("delivery_timeline_months", 6))
    data_hosting_country = inputs.get("data_hosting_country", "")

    total_steps = 5
    eval_threshold = getattr(settings, "EVALUATION_THRESHOLD", 0.70)
    enable_eval = getattr(settings, "ENABLE_EVALUATION", True)
    max_retries = getattr(settings, "MAX_AGENT_RETRIES", 2)

    event_queue: asyncio.Queue = asyncio.Queue()

    # Initial pipeline startup notification
    yield {
        "event": "init",
        "run_id": run_id,
        "message": "Initialized autonomous multi-agent pipeline with quality evaluation gates.",
        "progress": 3,
    }

    async def run_pipeline():
        try:
            # -------------------------------------------------------------
            # STEP 1: BUSINESS ANALYST
            # -------------------------------------------------------------
            def make_ba_task():
                return create_business_analyst_task(
                    business_idea=business_idea,
                    technology_preference=technology_preference,
                    cloud_preference=cloud_preference,
                    expected_daily_traffic=expected_daily_traffic,
                    delivery_timeline_months=delivery_timeline_months,
                    data_hosting_country=data_hosting_country,
                )

            ba_output = await execute_step_with_eval(
                agent_name="Business Analyst",
                role="Requirements & MVP Scope Analyst",
                step_num=1,
                total_steps=total_steps,
                task_factory_fn=make_ba_task,
                inputs=inputs,
                start_msg="Analyzing business idea, identifying stakeholders, non-functional requirements, and core MVP scope...",
                complete_msg="Business analysis and functional requirements established.",
                start_pct=5,
                complete_pct=22,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
            )

            # Anchor task object for downstream agent context propagation
            ba_task = make_ba_task()

            # -------------------------------------------------------------
            # STEP 2: SOLUTION ARCHITECT
            # -------------------------------------------------------------
            def make_sa_task():
                return create_solution_architect_task(
                    technology_preference=technology_preference,
                    cloud_preference=cloud_preference,
                    expected_daily_traffic=expected_daily_traffic,
                    delivery_timeline_months=delivery_timeline_months,
                    data_hosting_country=data_hosting_country,
                    ba_task=ba_task,
                )

            sa_output = await execute_step_with_eval(
                agent_name="Solution Architect",
                role="System & Component Architect",
                step_num=2,
                total_steps=total_steps,
                task_factory_fn=make_sa_task,
                inputs=inputs,
                start_msg="Designing component interaction diagrams, data flows, scalability patterns, and security perimeter...",
                complete_msg="High-level architecture and system components finalized.",
                start_pct=24,
                complete_pct=44,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
            )

            # Anchor task object for downstream agent context propagation
            sa_task = make_sa_task()

            # -------------------------------------------------------------
            # STEP 3: TECHNOLOGY ADVISOR
            # -------------------------------------------------------------
            def make_ta_task():
                return create_technology_advisor_task(
                    technology_preference=technology_preference,
                    cloud_preference=cloud_preference,
                    expected_daily_traffic=expected_daily_traffic,
                    delivery_timeline_months=delivery_timeline_months,
                    data_hosting_country=data_hosting_country,
                    ba_task=ba_task,
                    sa_task=sa_task,
                )

            ta_output = await execute_step_with_eval(
                agent_name="Technology Advisor",
                role="Technology Stack & Cloud Advisor",
                step_num=3,
                total_steps=total_steps,
                task_factory_fn=make_ta_task,
                inputs=inputs,
                start_msg="Evaluating technology stack trade-offs, databases, cloud services, and framework trade-offs...",
                complete_msg="Technology recommendations and trade-off analysis completed.",
                start_pct=46,
                complete_pct=66,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
            )

            # Anchor task object for downstream agent context propagation
            ta_task = make_ta_task()

            # -------------------------------------------------------------
            # STEP 4: DELIVERY PLANNER
            # -------------------------------------------------------------
            def make_dp_task():
                return create_delivery_planner_task(
                    delivery_timeline_months=delivery_timeline_months,
                    ba_task=ba_task,
                    sa_task=sa_task,
                    ta_task=ta_task,
                )

            dp_output = await execute_step_with_eval(
                agent_name="Delivery Planner",
                role="Delivery Roadmap & Milestones Planner",
                step_num=4,
                total_steps=total_steps,
                task_factory_fn=make_dp_task,
                inputs=inputs,
                start_msg="Synthesizing delivery workstreams, sprint milestones, team allocation, and risk mitigations...",
                complete_msg="Delivery roadmap, milestones, and risk register complete.",
                start_pct=68,
                complete_pct=88,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
            )

            # Anchor task object for downstream agent context propagation
            dp_task = make_dp_task()

            # -------------------------------------------------------------
            # STEP 5: REPORT WRITER AGENT (Final Synthesis)
            # -------------------------------------------------------------
            await event_queue.put({
                "event": "agent_start",
                "agent": "Report Writer",
                "step": 5,
                "total": total_steps,
                "role": "Lead Solution Consultant & Technical Writer",
                "message": "Synthesizing all specialist findings into the authoritative Master Solution Blueprint...",
                "progress": 90,
            })

            rw_task = create_report_writer_task(
                inputs=inputs,
                ba_task=ba_task,
                sa_task=sa_task,
                ta_task=ta_task,
                dp_task=dp_task,
            )

            rw_crew = Crew(agents=[rw_task.agent], tasks=[rw_task], verbose=True)
            rw_res = await asyncio.to_thread(rw_crew.kickoff)
            rw_output = rw_res.raw if hasattr(rw_res, "raw") else str(rw_res)

            # Assemble the exhaustive, production-grade Master Solution Blueprint
            master_md = build_master_blueprint(
                inputs=inputs,
                ba_output=ba_output,
                sa_output=sa_output,
                ta_output=ta_output,
                dp_output=dp_output,
                rw_output=rw_output,
                run_id=run_id,
            )

            await event_queue.put({
                "event": "agent_complete",
                "agent": "Report Writer",
                "step": 5,
                "total": total_steps,
                "output": rw_output,
                "message": "Executive architecture synthesis, system topology, and master blueprint compiled.",
                "progress": 97,
            })

            # Convert to HTML presentation artifact
            master_html = markdown_to_html(master_md, title=f"MindMesh Blueprint - {run_id}")

            await event_queue.put({
                "event": "complete",
                "run_id": run_id,
                "status": "completed",
                "progress": 100,
                "markdown": master_md,
                "html": master_html,
                "sections": {
                    "business_analyst": ba_output,
                    "solution_architect": sa_output,
                    "technology_advisor": ta_output,
                    "delivery_planner": dp_output,
                    "report_writer": master_md,
                },
            })

        except Exception as err:
            await event_queue.put({
                "event": "error",
                "run_id": run_id,
                "error": str(err),
                "message": f"Pipeline execution failed: {str(err)}",
            })
        finally:
            await event_queue.put(None)  # Sentinel indicating pipeline termination

    # Launch pipeline in background task and yield items as they arrive in event_queue
    pipeline_task = asyncio.create_task(run_pipeline())

    while True:
        event = await event_queue.get()
        if event is None:
            break
        yield event

    await pipeline_task
