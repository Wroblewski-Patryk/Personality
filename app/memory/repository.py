from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.memory.models import AionConclusion, AionMemory, AionProfile, AionReflectionTask, AionTheta, Base


class MemoryRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create_tables(self, engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def write_episode(
        self,
        event_id: str,
        trace_id: str,
        source: str,
        user_id: str,
        event_timestamp: datetime,
        summary: str,
        importance: float,
    ) -> dict:
        async with self.session_factory() as session:
            row = AionMemory(
                event_id=event_id,
                trace_id=trace_id,
                source=source,
                user_id=user_id,
                event_timestamp=event_timestamp,
                summary=summary,
                importance=importance,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)

        return {
            "id": row.id,
            "event_id": row.event_id,
            "timestamp": row.event_timestamp,
            "summary": row.summary,
            "importance": row.importance,
        }

    async def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionMemory)
                .where(AionMemory.user_id == user_id)
                .order_by(AionMemory.id.desc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [
            {
                "id": row.id,
                "event_id": row.event_id,
                "summary": row.summary,
                "importance": row.importance,
                "event_timestamp": row.event_timestamp,
            }
            for row in rows
        ]

    async def get_user_profile(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)

        if row is None:
            return None

        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "updated_at": row.updated_at,
        }

    async def get_user_theta(self, user_id: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionTheta, user_id)

        if row is None:
            return None

        return {
            "user_id": row.user_id,
            "support_bias": row.support_bias,
            "analysis_bias": row.analysis_bias,
            "execution_bias": row.execution_bias,
            "updated_at": row.updated_at,
        }

    async def get_user_runtime_preferences(self, user_id: str) -> dict:
        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(
                    AionConclusion.user_id == user_id,
                )
                .order_by(AionConclusion.updated_at.desc(), AionConclusion.id.desc())
                .limit(6)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        if not rows:
            return {}

        preferences: dict[str, object] = {}
        for row in rows:
            if row.kind == "response_style":
                preferences["response_style"] = row.content
                preferences["response_style_confidence"] = row.confidence
                preferences["response_style_source"] = row.source
                preferences["response_style_updated_at"] = row.updated_at
            elif row.kind == "preferred_role":
                preferences["preferred_role"] = row.content
                preferences["preferred_role_confidence"] = row.confidence
                preferences["preferred_role_source"] = row.source
                preferences["preferred_role_updated_at"] = row.updated_at

        return preferences

    async def get_user_conclusions(self, user_id: str, limit: int = 3) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(AionConclusion.user_id == user_id)
                .order_by(AionConclusion.updated_at.desc(), AionConclusion.id.desc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [
            {
                "id": row.id,
                "kind": row.kind,
                "content": row.content,
                "confidence": row.confidence,
                "source": row.source,
                "supporting_event_id": row.supporting_event_id,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]

    async def upsert_user_profile_language(
        self,
        user_id: str,
        language_code: str,
        confidence: float,
        source: str,
    ) -> dict:
        async with self.session_factory() as session:
            row = await session.get(AionProfile, user_id)
            if row is None:
                row = AionProfile(
                    user_id=user_id,
                    preferred_language=language_code,
                    language_confidence=confidence,
                    language_source=source,
                )
                session.add(row)
            elif self._should_update_language_profile(
                current_language=row.preferred_language,
                current_confidence=row.language_confidence,
                next_language=language_code,
                next_confidence=confidence,
                source=source,
            ):
                updated_confidence = self._next_language_confidence(
                    current_language=row.preferred_language,
                    current_confidence=row.language_confidence,
                    next_language=language_code,
                    next_confidence=confidence,
                )
                row.preferred_language = language_code
                row.language_confidence = updated_confidence
                row.language_source = source
            await session.commit()
            await session.refresh(row)

        return {
            "user_id": row.user_id,
            "preferred_language": row.preferred_language,
            "language_confidence": row.language_confidence,
            "language_source": row.language_source,
            "updated_at": row.updated_at,
        }

    async def upsert_conclusion(
        self,
        user_id: str,
        kind: str,
        content: str,
        confidence: float,
        source: str,
        supporting_event_id: str | None = None,
    ) -> dict:
        async with self.session_factory() as session:
            statement = (
                select(AionConclusion)
                .where(
                    AionConclusion.user_id == user_id,
                    AionConclusion.kind == kind,
                )
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionConclusion(
                    user_id=user_id,
                    kind=kind,
                    content=content,
                    confidence=confidence,
                    source=source,
                    supporting_event_id=supporting_event_id,
                )
                session.add(row)
            elif self._should_update_conclusion(
                current_content=row.content,
                current_confidence=row.confidence,
                next_content=content,
                next_confidence=confidence,
                source=source,
            ):
                updated_confidence = self._next_conclusion_confidence(
                    current_content=row.content,
                    current_confidence=row.confidence,
                    next_content=content,
                    next_confidence=confidence,
                )
                row.content = content
                row.confidence = updated_confidence
                row.source = source
                row.supporting_event_id = supporting_event_id

            await session.commit()
            await session.refresh(row)

        return {
            "user_id": row.user_id,
            "kind": row.kind,
            "content": row.content,
            "confidence": row.confidence,
            "source": row.source,
            "supporting_event_id": row.supporting_event_id,
            "updated_at": row.updated_at,
        }

    async def upsert_theta(
        self,
        user_id: str,
        support_bias: float,
        analysis_bias: float,
        execution_bias: float,
    ) -> dict:
        async with self.session_factory() as session:
            row = await session.get(AionTheta, user_id)
            if row is None:
                row = AionTheta(
                    user_id=user_id,
                    support_bias=support_bias,
                    analysis_bias=analysis_bias,
                    execution_bias=execution_bias,
                )
                session.add(row)
            else:
                row.support_bias = support_bias
                row.analysis_bias = analysis_bias
                row.execution_bias = execution_bias

            await session.commit()
            await session.refresh(row)

        return {
            "user_id": row.user_id,
            "support_bias": row.support_bias,
            "analysis_bias": row.analysis_bias,
            "execution_bias": row.execution_bias,
            "updated_at": row.updated_at,
        }

    async def enqueue_reflection_task(self, user_id: str, event_id: str) -> dict:
        async with self.session_factory() as session:
            statement = (
                select(AionReflectionTask)
                .where(AionReflectionTask.event_id == event_id)
                .limit(1)
            )
            result = await session.execute(statement)
            row = result.scalar_one_or_none()

            if row is None:
                row = AionReflectionTask(
                    user_id=user_id,
                    event_id=event_id,
                    status="pending",
                    attempts=0,
                    last_error=None,
                )
                session.add(row)
            elif row.status != "completed":
                row.user_id = user_id
                row.status = "pending"
                row.last_error = None

            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def get_pending_reflection_tasks(self, limit: int = 100) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionReflectionTask)
                .where(AionReflectionTask.status.in_(("pending", "processing", "failed")))
                .order_by(AionReflectionTask.id.asc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        return [self._serialize_reflection_task(row) for row in rows]

    async def mark_reflection_task_processing(self, task_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "processing"
            row.attempts += 1
            row.last_error = None
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def mark_reflection_task_completed(self, task_id: int) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "completed"
            row.last_error = None
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def mark_reflection_task_failed(self, task_id: int, error: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionReflectionTask, task_id)
            if row is None:
                return None
            row.status = "failed"
            row.last_error = error[:500]
            await session.commit()
            await session.refresh(row)

        return self._serialize_reflection_task(row)

    async def get_reflection_task_stats(
        self,
        *,
        max_attempts: int,
        stuck_after_seconds: int,
        retry_backoff_seconds: tuple[int, ...],
        now: datetime | None = None,
    ) -> dict[str, int]:
        async with self.session_factory() as session:
            statement = select(AionReflectionTask)
            result = await session.execute(statement)
            rows = result.scalars().all()

        current_time = self._coerce_datetime(now or datetime.now(timezone.utc))
        stats = {
            "total": 0,
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "retryable_failed": 0,
            "exhausted_failed": 0,
            "stuck_processing": 0,
        }
        for row in rows:
            stats["total"] += 1
            status = row.status
            if status in stats:
                stats[status] += 1

            attempts = int(row.attempts or 0)
            updated_at = self._coerce_datetime(row.updated_at)
            age_seconds = max(0.0, (current_time - updated_at).total_seconds()) if updated_at else 0.0

            if status == "processing" and age_seconds >= stuck_after_seconds:
                stats["stuck_processing"] += 1

            if status != "failed":
                continue

            if attempts >= max_attempts:
                stats["exhausted_failed"] += 1
                continue

            backoff = self._retry_backoff_seconds_for_attempts(attempts, retry_backoff_seconds)
            if age_seconds >= backoff:
                stats["retryable_failed"] += 1

        return stats

    def _should_update_language_profile(
        self,
        current_language: str,
        current_confidence: float,
        next_language: str,
        next_confidence: float,
        source: str,
    ) -> bool:
        if current_language == next_language:
            return True
        if source == "explicit_request":
            return True
        if next_confidence >= 0.9:
            return True
        return current_confidence <= 0.55 and next_confidence >= 0.72

    def _next_language_confidence(
        self,
        current_language: str,
        current_confidence: float,
        next_language: str,
        next_confidence: float,
    ) -> float:
        if current_language == next_language:
            return min(0.99, max(current_confidence, next_confidence))
        return next_confidence

    def _should_update_conclusion(
        self,
        current_content: str,
        current_confidence: float,
        next_content: str,
        next_confidence: float,
        source: str,
    ) -> bool:
        if current_content == next_content:
            return True
        if source == "explicit_request":
            return True
        return next_confidence >= current_confidence

    def _next_conclusion_confidence(
        self,
        current_content: str,
        current_confidence: float,
        next_content: str,
        next_confidence: float,
    ) -> float:
        if current_content == next_content:
            return min(0.99, max(current_confidence, next_confidence))
        return next_confidence

    def _serialize_reflection_task(self, row: AionReflectionTask) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "event_id": row.event_id,
            "status": row.status,
            "attempts": row.attempts,
            "last_error": row.last_error,
            "updated_at": row.updated_at,
            "created_at": row.created_at,
        }

    def _retry_backoff_seconds_for_attempts(self, attempts: int, retry_backoff_seconds: tuple[int, ...]) -> int:
        if attempts <= 0:
            return 0
        index = min(attempts - 1, len(retry_backoff_seconds) - 1)
        return retry_backoff_seconds[index]

    def _coerce_datetime(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
