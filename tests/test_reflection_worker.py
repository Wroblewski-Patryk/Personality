from app.reflection.worker import ReflectionWorker


class FakeMemoryRepository:
    def __init__(self, recent_memory: list[dict]):
        self.recent_memory = recent_memory
        self.conclusion_updates: list[dict] = []

    async def get_recent_for_user(self, user_id: str, limit: int = 8) -> list[dict]:
        return self.recent_memory[:limit]

    async def upsert_conclusion(self, **kwargs) -> dict:
        self.conclusion_updates.append(kwargs)
        return kwargs


async def test_reflection_worker_consolidates_explicit_preference_update_in_background() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {
                "summary": (
                    "event=Reply in bullet points from now on.; memory_kind=semantic; memory_topics=reply,bullet,points; "
                    "response_language=en; preference_update=response_style:structured; "
                    "action=success; expression=- first\\n- second"
                )
            }
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-1")

    assert result is True
    assert repository.conclusion_updates == [
        {
            "user_id": "u-1",
            "kind": "response_style",
            "content": "structured",
            "confidence": 0.98,
            "source": "background_reflection",
            "supporting_event_id": "evt-1",
        }
    ]


async def test_reflection_worker_infers_preferred_role_from_repeated_role_usage() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "role=executor; action=success; expression=Done one."},
            {"summary": "role=executor; action=success; expression=Done two."},
            {"summary": "role=executor; action=success; expression=Done three."},
            {"summary": "role=mentor; action=success; expression=Different path."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-role")

    assert result is True
    assert {
        "user_id": "u-1",
        "kind": "preferred_role",
        "content": "executor",
        "confidence": 0.76,
        "source": "background_reflection",
        "supporting_event_id": "evt-role",
    } in repository.conclusion_updates


async def test_reflection_worker_infers_concise_style_from_repeated_short_successful_outputs() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "action=success; expression=Short answer one."},
            {"summary": "action=success; expression=Short answer two."},
            {"summary": "action=success; expression=Short answer three."},
            {"summary": "action=success; expression=Another short answer."},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-2")

    assert result is True
    assert repository.conclusion_updates[0]["content"] == "concise"
    assert repository.conclusion_updates[0]["source"] == "background_reflection"


async def test_reflection_worker_skips_when_recent_memory_has_no_consistent_signal() -> None:
    repository = FakeMemoryRepository(
        recent_memory=[
            {"summary": "action=success; expression=This is a longer explanatory response that should not count as concise."},
            {"summary": "action=success; expression=- one\\n- two"},
        ]
    )
    worker = ReflectionWorker(memory_repository=repository)

    result = await worker.reflect_user(user_id="u-1", event_id="evt-3")

    assert result is False
    assert repository.conclusion_updates == []
