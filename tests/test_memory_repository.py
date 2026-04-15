from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.memory.models import AionReflectionTask
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
