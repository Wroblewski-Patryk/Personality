from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.memory.models import AionConclusion, AionGoal, AionGoalProgress, AionReflectionTask, AionTask
from app.memory.repository import MemoryRepository


async def test_memory_repository_reports_reflection_task_stats(tmp_path) -> None:
    database_path = tmp_path / "memory-repository.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    pending = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-pending")
    processing = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-processing")
    retryable_failed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-retryable")
    exhausted_failed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-exhausted")
    completed = await repository.enqueue_reflection_task(user_id="u-1", event_id="evt-completed")

    await repository.mark_reflection_task_processing(task_id=int(processing["id"]))
    await repository.mark_reflection_task_processing(task_id=int(retryable_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(retryable_failed["id"]), error="temporary issue")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="still failing")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="final failure")
    await repository.mark_reflection_task_processing(task_id=int(exhausted_failed["id"]))
    await repository.mark_reflection_task_failed(task_id=int(exhausted_failed["id"]), error="final final failure")
    await repository.mark_reflection_task_processing(task_id=int(completed["id"]))
    await repository.mark_reflection_task_completed(task_id=int(completed["id"]))

    now = datetime.now(timezone.utc)
    async with session_factory() as session:
        processing_row = await session.get(AionReflectionTask, int(processing["id"]))
        retryable_failed_row = await session.get(AionReflectionTask, int(retryable_failed["id"]))
        exhausted_failed_row = await session.get(AionReflectionTask, int(exhausted_failed["id"]))
        pending_row = await session.get(AionReflectionTask, int(pending["id"]))
        assert processing_row is not None
        assert retryable_failed_row is not None
        assert exhausted_failed_row is not None
        assert pending_row is not None
        processing_row.updated_at = now - timedelta(seconds=240)
        retryable_failed_row.updated_at = now - timedelta(seconds=40)
        exhausted_failed_row.updated_at = now - timedelta(minutes=5)
        pending_row.updated_at = now - timedelta(seconds=10)
        await session.commit()

    stats = await repository.get_reflection_task_stats(
        max_attempts=3,
        stuck_after_seconds=180,
        retry_backoff_seconds=(5, 30, 120),
        now=now,
    )

    assert stats == {
        "total": 5,
        "pending": 1,
        "processing": 1,
        "completed": 1,
        "failed": 2,
        "retryable_failed": 1,
        "exhausted_failed": 1,
        "stuck_processing": 1,
    }

    async with session_factory() as session:
        result = await session.execute(select(AionReflectionTask).order_by(AionReflectionTask.id.asc()))
        rows = result.scalars().all()

    assert [row.status for row in rows] == ["pending", "processing", "failed", "failed", "completed"]

    await engine.dispose()


async def test_memory_repository_upserts_and_loads_active_goals_and_tasks(tmp_path) -> None:
    database_path = tmp_path / "memory-goals.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    goal = await repository.upsert_active_goal(
        user_id="u-1",
        name="ship the MVP this week",
        description="User-declared goal: ship the MVP this week",
        priority="high",
        goal_type="operational",
    )
    task = await repository.upsert_active_task(
        user_id="u-1",
        goal_id=int(goal["id"]),
        name="fix deployment blocker",
        description="User-declared task: fix deployment blocker",
        priority="high",
        status="blocked",
    )

    goals = await repository.get_active_goals(user_id="u-1", limit=5)
    tasks = await repository.get_active_tasks(user_id="u-1", goal_ids=[int(goal["id"])], limit=5)

    assert goals[0]["name"] == "ship the MVP this week"
    assert goals[0]["priority"] == "high"
    assert tasks[0]["name"] == "fix deployment blocker"
    assert tasks[0]["goal_id"] == goal["id"]
    assert tasks[0]["status"] == "blocked"

    async with session_factory() as session:
        goal_rows = (await session.execute(select(AionGoal))).scalars().all()
        task_rows = (await session.execute(select(AionTask))).scalars().all()

    assert len(goal_rows) == 1
    assert len(task_rows) == 1

    await engine.dispose()


async def test_memory_repository_updates_task_status_and_removes_done_from_active_list(tmp_path) -> None:
    database_path = tmp_path / "memory-task-status.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    task = await repository.upsert_active_task(
        user_id="u-1",
        name="fix deployment blocker",
        description="User-declared task: fix deployment blocker",
        priority="high",
        status="blocked",
    )

    updated = await repository.update_task_status(task_id=int(task["id"]), status="done")
    active_tasks = await repository.get_active_tasks(user_id="u-1", limit=5)

    assert updated is not None
    assert updated["status"] == "done"
    assert active_tasks == []

    async with session_factory() as session:
        task_row = await session.get(AionTask, int(task["id"]))

    assert task_row is not None
    assert task_row.status == "done"

    await engine.dispose()


async def test_memory_repository_exposes_goal_execution_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-execution-state.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_execution_state",
                content="blocked",
                confidence=0.82,
                source="background_reflection",
                supporting_event_id="evt-goal-blocked",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_execution_state"] == "blocked"
    assert preferences["goal_execution_state_confidence"] == 0.82
    assert preferences["goal_execution_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_allows_dynamic_goal_execution_state_transition(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-execution-transition.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="blocked",
        confidence=0.82,
        source="background_reflection",
        supporting_event_id="evt-blocked",
    )
    updated = await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_execution_state",
        content="progressing",
        confidence=0.76,
        source="background_reflection",
        supporting_event_id="evt-progressing",
    )

    assert updated["content"] == "progressing"
    assert updated["confidence"] == 0.76
    assert updated["supporting_event_id"] == "evt-progressing"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_score_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-score.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_score",
                content="0.84",
                confidence=0.74,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-score",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_score"] == 0.84
    assert preferences["goal_progress_score_confidence"] == 0.74
    assert preferences["goal_progress_score_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_trend_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-trend.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_trend",
                content="improving",
                confidence=0.73,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-trend",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_trend"] == "improving"
    assert preferences["goal_progress_trend_confidence"] == 0.73
    assert preferences["goal_progress_trend_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_transition_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-transition.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_transition",
                content="entered_completion_window",
                confidence=0.77,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-transition",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_transition"] == "entered_completion_window"
    assert preferences["goal_milestone_transition_confidence"] == 0.77
    assert preferences["goal_milestone_transition_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_allows_dynamic_goal_milestone_transition_updates(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-dynamic.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_milestone_transition",
        content="entered_completion_window",
        confidence=0.77,
        source="background_reflection",
        supporting_event_id="evt-entered-completion",
    )
    updated = await repository.upsert_conclusion(
        user_id="u-1",
        kind="goal_milestone_transition",
        content="slipped_from_completion_window",
        confidence=0.78,
        source="background_reflection",
        supporting_event_id="evt-slipped-completion",
    )

    assert updated["content"] == "slipped_from_completion_window"
    assert updated["confidence"] == 0.78
    assert updated["supporting_event_id"] == "evt-slipped-completion"

    await engine.dispose()


async def test_memory_repository_exposes_goal_milestone_state_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-milestone-state.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_milestone_state",
                content="completion_window",
                confidence=0.8,
                source="background_reflection",
                supporting_event_id="evt-goal-milestone-state",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_milestone_state"] == "completion_window"
    assert preferences["goal_milestone_state_confidence"] == 0.8
    assert preferences["goal_milestone_state_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_exposes_goal_progress_arc_in_runtime_preferences(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-arc.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    async with session_factory() as session:
        session.add(
            AionConclusion(
                user_id="u-1",
                kind="goal_progress_arc",
                content="recovery_gaining_traction",
                confidence=0.76,
                source="background_reflection",
                supporting_event_id="evt-goal-progress-arc",
            )
        )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["goal_progress_arc"] == "recovery_gaining_traction"
    assert preferences["goal_progress_arc_confidence"] == 0.76
    assert preferences["goal_progress_arc_source"] == "background_reflection"

    await engine.dispose()


async def test_memory_repository_runtime_preferences_can_hold_more_than_six_kinds(tmp_path) -> None:
    database_path = tmp_path / "memory-runtime-preferences-limit.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    rows = [
        ("response_style", "structured", 0.95),
        ("preferred_role", "analyst", 0.76),
        ("collaboration_preference", "guided", 0.73),
        ("goal_execution_state", "recovering", 0.77),
        ("goal_progress_score", "0.61", 0.74),
        ("goal_progress_trend", "improving", 0.73),
        ("goal_progress_arc", "recovery_gaining_traction", 0.76),
    ]
    async with session_factory() as session:
        for index, (kind, content, confidence) in enumerate(rows, start=1):
            session.add(
                AionConclusion(
                    user_id="u-1",
                    kind=kind,
                    content=content,
                    confidence=confidence,
                    source="background_reflection",
                    supporting_event_id=f"evt-{index}",
                )
            )
        await session.commit()

    preferences = await repository.get_user_runtime_preferences(user_id="u-1")

    assert preferences["response_style"] == "structured"
    assert preferences["preferred_role"] == "analyst"
    assert preferences["collaboration_preference"] == "guided"
    assert preferences["goal_execution_state"] == "recovering"
    assert preferences["goal_progress_score"] == 0.61
    assert preferences["goal_progress_trend"] == "improving"
    assert preferences["goal_progress_arc"] == "recovery_gaining_traction"

    await engine.dispose()


async def test_memory_repository_appends_and_reads_goal_progress_history(tmp_path) -> None:
    database_path = tmp_path / "memory-goal-progress-history.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    repository = MemoryRepository(session_factory=session_factory)
    await repository.create_tables(engine)

    first = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.28,
        execution_state="blocked",
        progress_trend="slipping",
        source_event_id="evt-1",
    )
    second = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.28,
        execution_state="blocked",
        progress_trend="slipping",
        source_event_id="evt-2",
    )
    third = await repository.append_goal_progress_snapshot(
        user_id="u-1",
        goal_id=11,
        score=0.61,
        execution_state="recovering",
        progress_trend="improving",
        source_event_id="evt-3",
    )

    history = await repository.get_recent_goal_progress(user_id="u-1", goal_ids=[11], limit=5)

    assert first["id"] == second["id"]
    assert third["score"] == 0.61
    assert [item["score"] for item in history] == [0.61, 0.28]
    assert history[0]["progress_trend"] == "improving"

    async with session_factory() as session:
        rows = (await session.execute(select(AionGoalProgress).order_by(AionGoalProgress.id.asc()))).scalars().all()

    assert len(rows) == 2

    await engine.dispose()
