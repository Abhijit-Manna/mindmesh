import asyncio
import traceback
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


async def _kickoff_with_retries(
    crew: Crew,
    max_attempts: int,
    timeout_seconds: int,
    on_retry: Callable[[int, int, Exception], Any] | None = None,
) -> Any:
    """Run a CrewAI kickoff with bounded timeout and provider retries."""
    attempts = max(1, max_attempts)
    timeout = max(1, timeout_seconds)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(crew.kickoff),
                timeout=timeout,
            )
        except (Exception, asyncio.TimeoutError) as exc:
            last_error = exc
            if attempt == attempts:
                raise
            if on_retry is not None:
                await on_retry(attempt, attempts, exc)
            await asyncio.sleep(min(2 ** (attempt - 1), 8))

    raise RuntimeError("LLM kickoff failed without an exception.") from last_error


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
    upstream_context: str = "",
) -> str:
    """
    Execute one specialist agent with an optional evaluator quality gate.

    The same Task object is reused across retries so evaluator remediation
    updates the actual task being retried.
    """
    task = task_factory_fn()
    base_task_description = task.description

    retries = 0
    final_output = ""
    provider_attempts = max(1, max_retries + 1)
    timeout_seconds = getattr(settings, "AGENT_TIMEOUT_SECONDS", 120)

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
        async def notify_agent_retry(
            attempt: int,
            attempts: int,
            error: Exception,
        ) -> None:
            await event_queue.put({
                "event": "agent_retry",
                "agent": agent_name,
                "step": step_num,
                "retry_count": attempt,
                "message": (
                    f"{agent_name} LLM call failed; retrying "
                    f"(Attempt {attempt + 1}/{attempts}): {error}"
                ),
                "progress": start_pct + 1,
            })

        res = await _kickoff_with_retries(
            crew=crew,
            max_attempts=provider_attempts,
            timeout_seconds=timeout_seconds,
            on_retry=notify_agent_retry,
        )
        raw_output = getattr(res, "raw", res)
        final_output = str(raw_output or "").strip()

        if not enable_eval:
            break

        # Run evaluation gate
        await event_queue.put({
            "event": "evaluation_start",
            "agent": agent_name,
            "step": step_num,
            "total": total_steps,
            "message": (f"Quality Auditor evaluating {agent_name} "
                        "output against role criteria..."),
            "progress": start_pct + 3,
        })

        async def notify_evaluator_retry(
            attempt: int,
            attempts: int,
            error: Exception,
        ) -> None:
            await event_queue.put({
                "event": "agent_retry",
                "agent": agent_name,
                "step": step_num,
                "retry_count": attempt,
                "message": (
                    f"Evaluator call failed; retrying "
                    f"(Attempt {attempt + 1}/{attempts}): {error}"
                ),
                "progress": start_pct + 4,
            })

        async def evaluate_with_retries() -> Dict[str, Any]:
            eval_attempts = max(1, max_retries + 1)
            last_error: Exception | None = None
            for attempt in range(1, eval_attempts + 1):
                try:
                    return await asyncio.wait_for(
                        evaluate_agent_output(
                            agent_role=agent_name,
                            agent_output=final_output,
                            inputs=inputs,
                            threshold=eval_threshold,
                            upstream_context=upstream_context,
                        ),
                        timeout=timeout_seconds,
                    )
                except (Exception, asyncio.TimeoutError) as exc:
                    last_error = exc
                    if attempt == eval_attempts:
                        raise
                    await notify_evaluator_retry(attempt, eval_attempts, exc)
                    await asyncio.sleep(min(2 ** (attempt - 1), 8))
            raise RuntimeError("Evaluator failed without an exception.") from last_error

        eval_res = await evaluate_with_retries()
        if not isinstance(eval_res, dict):
            raise TypeError(
                f"Evaluator returned an invalid result type: "
                f"{type(eval_res).__name__}"
            )

        try:
            score = float(eval_res.get("score", 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0

        raw_passed = eval_res.get("passed", False)

        if isinstance(raw_passed, bool):
            passed = raw_passed
        elif isinstance(raw_passed, str):
            passed = raw_passed.strip().lower() == "true"
        else:
            passed = False

        await event_queue.put({
            "event": "evaluation",
            "agent": agent_name,
            "step": step_num,
            "score": score,
            "passed": passed,
            "summary": eval_res.get("summary", ""),
            "critique": eval_res.get("critique", []),
            "remediation": eval_res.get("remediation_guidance", ""),
            "message": (f"Evaluator Score: {score:.2f} — "
                        f"{'Accepted' if passed else 'Refinement Suggested'}"),
            "progress": start_pct + 6,
        })

        if passed or retries >= max_retries:
            break

        retries += 1
        remediation_guidance = str(
            eval_res.get("remediation_guidance", "") or ""
        ).strip()

        if remediation_guidance and remediation_guidance.lower() != "none":
            task.description = (
                base_task_description
                + "\n\n"
                + "==============================================================\n"
                + "LATEST EVALUATOR REMEDIATION\n"
                + "==============================================================\n"
                + remediation_guidance
                + "\n\n"
                + "Revise the deliverable according to this evaluator feedback.\n"
                + "Preserve valid work and correct the identified deficiencies.\n"
                + "The user's original requirements and constraints remain the "
                  "highest priority."
            )

        await event_queue.put({
            "event": "agent_retry",
            "agent": agent_name,
            "step": step_num,
            "retry_count": retries,
            "message": (f"Refining {agent_name} output based on evaluator critique "
                        f"(Attempt {retries}/{max_retries})..."),
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
            
            ba_task = None

            def make_ba_task():
                nonlocal ba_task

                if ba_task is None:
                    ba_task = create_business_analyst_task(
                        business_idea=business_idea,
                        technology_preference=technology_preference,
                        cloud_preference=cloud_preference,
                        expected_daily_traffic=expected_daily_traffic,
                        delivery_timeline_months=delivery_timeline_months,
                        data_hosting_country=data_hosting_country,
                    )

                return ba_task

            ba_output = await execute_step_with_eval(
                agent_name="Business Analyst",
                role="Requirements & MVP Scope Analyst",
                step_num=1,
                total_steps=total_steps,
                task_factory_fn=make_ba_task,
                inputs=inputs,
                start_msg=("Analyzing business idea, identifying stakeholders, "
                           "non-functional requirements, and core MVP scope..."),
                complete_msg="Business analysis and functional requirements established.",
                start_pct=5,
                complete_pct=22,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
                upstream_context="",
            )

           

            # -------------------------------------------------------------
            # STEP 2: SOLUTION ARCHITECT
            # -------------------------------------------------------------
            sa_task = None

            def make_sa_task():
                nonlocal sa_task

                if sa_task is None:
                    sa_task = create_solution_architect_task(
                        technology_preference=technology_preference,
                        cloud_preference=cloud_preference,
                        expected_daily_traffic=expected_daily_traffic,
                        delivery_timeline_months=delivery_timeline_months,
                        data_hosting_country=data_hosting_country,
                        ba_task=ba_task,
                    )

                return sa_task

            sa_output = await execute_step_with_eval(
                agent_name="Solution Architect",
                role="System & Component Architect",
                step_num=2,
                total_steps=total_steps,
                task_factory_fn=make_sa_task,
                inputs=inputs,
                start_msg=(
                    "Designing component interaction diagrams, data flows, "
                    "scalability patterns, and security perimeter..."
                ),
                complete_msg="High-level architecture and system components finalized.",
                start_pct=24,
                complete_pct=44,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
                upstream_context=(
                    "BUSINESS ANALYST OUTPUT:\n\n"
                    + ba_output
                ),
            )


            # -------------------------------------------------------------
            # STEP 3: TECHNOLOGY ADVISOR
            # -------------------------------------------------------------
            ta_task = None

            def make_ta_task():
                nonlocal ta_task

                if ta_task is None: 
                    ta_task = create_technology_advisor_task(
                        technology_preference=technology_preference,
                        cloud_preference=cloud_preference,
                        expected_daily_traffic=expected_daily_traffic,
                        delivery_timeline_months=delivery_timeline_months,
                        data_hosting_country=data_hosting_country,
                        ba_task=ba_task,
                        sa_task=sa_task,
                    )

                return ta_task  

            ta_output = await execute_step_with_eval(
                agent_name="Technology Advisor",
                role="Technology Stack & Cloud Advisor",
                step_num=3,
                total_steps=total_steps,
                task_factory_fn=make_ta_task,
                inputs=inputs,
                start_msg=(
                    "Evaluating technology stack trade-offs, databases, "
                    "cloud services, and framework trade-offs..."
                ),
                complete_msg="Technology recommendations and trade-off analysis completed.",
                start_pct=46,
                complete_pct=66,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
                upstream_context=(
                    "SOLUTION ARCHITECT OUTPUT:\n\n"
                    + sa_output
                ),
            )

            

            # -------------------------------------------------------------
            # STEP 4: DELIVERY PLANNER
            # -------------------------------------------------------------
            dp_task = None

            def make_dp_task():
                nonlocal dp_task

                if dp_task is None:
                    dp_task = create_delivery_planner_task(
                        delivery_timeline_months=delivery_timeline_months,
                        ba_task=ba_task,
                        sa_task=sa_task,
                        ta_task=ta_task,
                    )

                return dp_task

            dp_output = await execute_step_with_eval(
                agent_name="Delivery Planner",
                role="Delivery Roadmap & Milestones Planner",
                step_num=4,
                total_steps=total_steps,
                task_factory_fn=make_dp_task,
                inputs=inputs,
                start_msg=(
                    "Synthesizing delivery workstreams, sprint milestones, "
                    "team allocation, and risk mitigations..."
                ),
                complete_msg="Delivery roadmap, milestones, and risk register complete.",
                start_pct=68,
                complete_pct=88,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
                upstream_context=(
                    "SOLUTION ARCHITECT OUTPUT:\n\n"
                    + sa_output
                    + "\n\n"
                    + "TECHNOLOGY ADVISOR OUTPUT:\n\n"
                    + ta_output
                    ),
            )

            

            # -------------------------------------------------------------
            # STEP 5: REPORT WRITER AGENT (Final Synthesis)
            # -------------------------------------------------------------
            def make_rw_task():
                return create_report_writer_task(
                    inputs=inputs,
                    ba_task=ba_task,
                    sa_task=sa_task,
                    ta_task=ta_task,
                    dp_task=dp_task,
                    ba_output=ba_output,
                    sa_output=sa_output,
                    ta_output=ta_output,
                    dp_output=dp_output,
                )

            rw_output = await execute_step_with_eval(
                agent_name="Report Writer",
                role="Lead Solution Consultant & Technical Writer",
                step_num=5,
                total_steps=total_steps,
                task_factory_fn=make_rw_task,
                inputs=inputs,
                start_msg=(
                    "Synthesizing all specialist findings into the authoritative "
                    "Master Solution Blueprint..."
                ),
                complete_msg=(
                    "Final solution blueprint synthesized and quality-checked."
                ),
                start_pct=90,
                complete_pct=97,
                event_queue=event_queue,
                enable_eval=enable_eval,
                eval_threshold=eval_threshold,
                max_retries=max_retries,
                upstream_context=(
                    "BUSINESS ANALYST OUTPUT:\n\n"
                    + ba_output
                    + "\n\nSOLUTION ARCHITECT OUTPUT:\n\n"
                    + sa_output
                    + "\n\nTECHNOLOGY ADVISOR OUTPUT:\n\n"
                    + ta_output
                    + "\n\nDELIVERY PLANNER OUTPUT:\n\n"
                    + dp_output
                ),
            )
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
            master_html = await asyncio.to_thread(
                markdown_to_html,
                master_md,
                title=f"MindMesh Blueprint - {run_id}",
            )

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
            traceback_text = traceback.format_exc()
            print(
                f"[pipeline] run_id={run_id} failed with traceback:\n"
                f"{traceback_text}"
            )
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
