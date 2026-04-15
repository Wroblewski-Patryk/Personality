from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.memory.models import AionConclusion, AionMemory, AionProfile, Base


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
