from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.memory.models import (
    AionConclusion,
    AionGoal,
    AionGoalProgress,
    AionMemory,
    AionProfile,
    AionReflectionTask,
    AionTask,
    AionTheta,
    Base,
)


class MemoryRepository:
    ACTIVE_GOAL_STATUSES = ("active",)
    ACTIVE_TASK_STATUSES = ("todo", "in_progress", "blocked")

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

    async def get_active_goals(self, user_id: str, limit: int = 5) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoal)
                .where(
                    AionGoal.user_id == user_id,
                    AionGoal.status.in_(self.ACTIVE_GOAL_STATUSES),
                )
                .order_by(AionGoal.updated_at.desc(), AionGoal.id.desc())
                .limit(limit)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        rows = sorted(
            rows,
            key=lambda row: (
                self._goal_priority_rank(row.priority),
                self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc),
                row.id,
            ),
            reverse=True,
        )
        return [self._serialize_goal(row) for row in rows[:limit]]

    async def get_active_tasks(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 5,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionTask)
                .where(
                    AionTask.user_id == user_id,
                    AionTask.status.in_(self.ACTIVE_TASK_STATUSES),
                )
                .order_by(AionTask.updated_at.desc(), AionTask.id.desc())
                .limit(max(limit * 2, limit))
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            goal_linked = [row for row in rows if row.goal_id in goal_id_set]
            unlinked = [row for row in rows if row.goal_id not in goal_id_set]
            rows = goal_linked + unlinked

        rows = sorted(
            rows,
            key=lambda row: (
                self._task_status_rank(row.status),
                self._task_priority_rank(row.priority),
                self._coerce_datetime(row.updated_at) or datetime.min.replace(tzinfo=timezone.utc),
                row.id,
            ),
            reverse=True,
        )
        return [self._serialize_task(row) for row in rows[:limit]]

    async def get_recent_goal_progress(
        self,
        user_id: str,
        *,
        goal_ids: list[int] | None = None,
        limit: int = 6,
    ) -> list[dict]:
        async with self.session_factory() as session:
            statement = (
                select(AionGoalProgress)
                .where(AionGoalProgress.user_id == user_id)
                .order_by(AionGoalProgress.created_at.desc(), AionGoalProgress.id.desc())
                .limit(limit * 3)
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

        goal_id_set = {goal_id for goal_id in (goal_ids or []) if goal_id is not None}
        if goal_id_set:
            rows = [row for row in rows if int(row.goal_id) in goal_id_set]

        return [self._serialize_goal_progress(row) for row in rows[:limit]]

    async def upsert_active_goal(
        self,
        *,
        user_id: str,
        name: str,
        description: str,
        priority: str = "medium",
        goal_type: str = "tactical",
    ) -> dict:
        normalized_name = self._normalize_match_text(name)
        async with self.session_factory() as session:
            statement = (
                select(AionGoal)
                .where(
                    AionGoal.user_id == user_id,
                    AionGoal.status.in_(("active", "paused")),
                )
                .order_by(AionGoal.updated_at.desc(), AionGoal.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            row = next(
                (
                    item
                    for item in rows
                    if self._normalize_match_text(item.name) == normalized_name
                ),
                None,
            )

            if row is None:
                row = AionGoal(
                    user_id=user_id,
                    name=name[:160],
                    description=description[:500],
                    priority=priority,
                    status="active",
                    goal_type=goal_type,
                )
                session.add(row)
            else:
                row.name = name[:160]
                row.description = description[:500]
                row.priority = priority
                row.status = "active"
                row.goal_type = goal_type

            await session.commit()
            await session.refresh(row)

        return self._serialize_goal(row)

    async def upsert_active_task(
        self,
        *,
        user_id: str,
        name: str,
        description: str,
        priority: str = "medium",
        goal_id: int | None = None,
        status: str = "todo",
    ) -> dict:
        normalized_name = self._normalize_match_text(name)
        async with self.session_factory() as session:
            statement = (
                select(AionTask)
                .where(
                    AionTask.user_id == user_id,
                    AionTask.status.in_(self.ACTIVE_TASK_STATUSES),
                )
                .order_by(AionTask.updated_at.desc(), AionTask.id.desc())
            )
            result = await session.execute(statement)
            rows = result.scalars().all()

            row = next(
                (
                    item
                    for item in rows
                    if self._normalize_match_text(item.name) == normalized_name
                    and (goal_id is None or item.goal_id == goal_id or item.goal_id is None)
                ),
                None,
            )

            if row is None:
                row = AionTask(
                    user_id=user_id,
                    goal_id=goal_id,
                    name=name[:160],
                    description=description[:500],
                    priority=priority,
                    status=status,
                )
                session.add(row)
            else:
                row.goal_id = goal_id if goal_id is not None else row.goal_id
                row.name = name[:160]
                row.description = description[:500]
                row.priority = priority
                row.status = status

            await session.commit()
            await session.refresh(row)

        return self._serialize_task(row)

    async def update_task_status(self, *, task_id: int, status: str) -> dict | None:
        async with self.session_factory() as session:
            row = await session.get(AionTask, task_id)
            if row is None:
                return None
            row.status = status
            await session.commit()
            await session.refresh(row)

        return self._serialize_task(row)

    async def append_goal_progress_snapshot(
        self,
        *,
        user_id: str,
        goal_id: int,
        score: float,
        execution_state: str | None,
        progress_trend: str | None,
        source_event_id: str | None = None,
    ) -> dict:
        normalized_score = round(max(0.0, min(1.0, score)), 2)
        async with self.session_factory() as session:
            latest_statement = (
                select(AionGoalProgress)
                .where(
                    AionGoalProgress.user_id == user_id,
                    AionGoalProgress.goal_id == goal_id,
                )
                .order_by(AionGoalProgress.created_at.desc(), AionGoalProgress.id.desc())
                .limit(1)
            )
            latest_result = await session.execute(latest_statement)
            latest_row = latest_result.scalar_one_or_none()

            if (
                latest_row is not None
                and abs(float(latest_row.score) - normalized_score) < 0.01
                and (latest_row.execution_state or "") == (execution_state or "")
                and (latest_row.progress_trend or "") == (progress_trend or "")
            ):
                return self._serialize_goal_progress(latest_row)

            row = AionGoalProgress(
                user_id=user_id,
                goal_id=goal_id,
                score=normalized_score,
                execution_state=execution_state,
                progress_trend=progress_trend,
                source_event_id=source_event_id,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)

        return self._serialize_goal_progress(row)

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
            elif row.kind == "collaboration_preference":
                preferences["collaboration_preference"] = row.content
                preferences["collaboration_preference_confidence"] = row.confidence
                preferences["collaboration_preference_source"] = row.source
                preferences["collaboration_preference_updated_at"] = row.updated_at
            elif row.kind == "goal_execution_state":
                preferences["goal_execution_state"] = row.content
                preferences["goal_execution_state_confidence"] = row.confidence
                preferences["goal_execution_state_source"] = row.source
                preferences["goal_execution_state_updated_at"] = row.updated_at
            elif row.kind == "goal_progress_score":
                try:
                    preferences["goal_progress_score"] = float(row.content)
                except ValueError:
                    continue
                preferences["goal_progress_score_confidence"] = row.confidence
                preferences["goal_progress_score_source"] = row.source
                preferences["goal_progress_score_updated_at"] = row.updated_at
            elif row.kind == "goal_progress_trend":
                preferences["goal_progress_trend"] = row.content
                preferences["goal_progress_trend_confidence"] = row.confidence
                preferences["goal_progress_trend_source"] = row.source
                preferences["goal_progress_trend_updated_at"] = row.updated_at

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
                kind=kind,
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
        kind: str,
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
        if kind in {"goal_execution_state", "goal_progress_score", "goal_progress_trend"}:
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

    def _serialize_goal(self, row: AionGoal) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "name": row.name,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "goal_type": row.goal_type,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _serialize_task(self, row: AionTask) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "name": row.name,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _serialize_goal_progress(self, row: AionGoalProgress) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "goal_id": row.goal_id,
            "score": row.score,
            "execution_state": row.execution_state,
            "progress_trend": row.progress_trend,
            "source_event_id": row.source_event_id,
            "created_at": row.created_at,
        }

    def _goal_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }.get(priority, 0)

    def _task_priority_rank(self, priority: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
        }.get(priority, 0)

    def _task_status_rank(self, status: str) -> int:
        return {
            "todo": 1,
            "in_progress": 2,
            "blocked": 3,
        }.get(status, 0)

    def _normalize_match_text(self, value: str) -> str:
        lowered = " ".join(value.strip().lower().split())
        return "".join(char if char.isalnum() or char.isspace() else " " for char in lowered).strip()

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
