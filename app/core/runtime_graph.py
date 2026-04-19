from time import perf_counter
from typing import Any, Awaitable, Callable, TypeVar

from langgraph.graph import END, START, StateGraph

from app.core.graph_adapters import GraphStageAdapters
from app.core.graph_state import GraphRuntimeState, expression_to_action_delivery
from app.core.logging import RuntimeStageLogger

T = TypeVar("T")


class ForegroundLangGraphRunner:
    """Runs the foreground cognitive stages through a LangGraph state graph."""

    def __init__(self, adapters: GraphStageAdapters):
        self.adapters = adapters
        self._graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(dict[str, Any])
        builder.add_node("perception", self._perception_node)
        builder.add_node("affective_assessment", self._affective_node)
        builder.add_node("context", self._context_node)
        builder.add_node("motivation", self._motivation_node)
        builder.add_node("role", self._role_node)
        builder.add_node("planning", self._planning_node)
        builder.add_node("expression", self._expression_node)
        builder.add_node("action", self._action_node)

        builder.add_edge(START, "perception")
        builder.add_edge("perception", "affective_assessment")
        builder.add_edge("affective_assessment", "context")
        builder.add_edge("context", "motivation")
        builder.add_edge("motivation", "role")
        builder.add_edge("role", "planning")
        builder.add_edge("planning", "expression")
        builder.add_edge("expression", "action")
        builder.add_edge("action", END)
        return builder.compile()

    def _present_label(self, value: object | None) -> str:
        return "yes" if value else "no"

    def _runtime_ctx(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = state.get("_runtime")
        if not isinstance(runtime_ctx, dict):
            raise ValueError("graph runtime context is missing")
        return runtime_ctx

    def _graph_state(self, state: dict[str, Any]) -> GraphRuntimeState:
        graph_state = state.get("graph_state")
        if not isinstance(graph_state, GraphRuntimeState):
            raise ValueError("graph_state is missing or invalid")
        return graph_state

    def _run_stage(
        self,
        *,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        stage: str,
        input_summary: str,
        operation: Callable[[], T],
        output_summary: Callable[[T], str],
    ) -> T:
        stage_logger.start(stage, summary=input_summary)
        started = perf_counter()
        try:
            result = operation()
        except Exception as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            stage_timings_ms[stage] = duration_ms
            stage_logger.failure(stage, duration_ms=duration_ms, error=exc, summary=input_summary)
            raise

        duration_ms = int((perf_counter() - started) * 1000)
        stage_timings_ms[stage] = duration_ms
        stage_logger.success(stage, duration_ms=duration_ms, summary=output_summary(result))
        return result

    async def _run_async_stage(
        self,
        *,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        stage: str,
        input_summary: str,
        operation: Callable[[], Awaitable[T]],
        output_summary: Callable[[T], str],
    ) -> T:
        stage_logger.start(stage, summary=input_summary)
        started = perf_counter()
        try:
            result = await operation()
        except Exception as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            stage_timings_ms[stage] = duration_ms
            stage_logger.failure(stage, duration_ms=duration_ms, error=exc, summary=input_summary)
            raise

        duration_ms = int((perf_counter() - started) * 1000)
        stage_timings_ms[stage] = duration_ms
        stage_logger.success(stage, duration_ms=duration_ms, summary=output_summary(result))
        return result

    def _perception_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        text = runtime_ctx["text"]
        user_profile = runtime_ctx["user_profile"]
        graph_state = self._graph_state(state)
        updated = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="perception",
            input_summary=(
                f"text_len={len(text)} recent_memory={len(graph_state.memory.episodic)} "
                f"profile={self._present_label(user_profile)}"
            ),
            operation=lambda: self.adapters.run_perception(graph_state),
            output_summary=lambda result: (
                f"topic={result.perception.topic} intent={result.perception.intent} "
                f"language={result.perception.language} "
                f"affect={result.perception.affective.affect_label} "
                f"ambiguity={result.perception.ambiguity}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    async def _affective_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        text = runtime_ctx["text"]
        graph_state = self._graph_state(state)
        perception = graph_state.perception
        assert perception is not None
        updated = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="affective_assessment",
            input_summary=(
                f"text_len={len(text)} language={perception.language} "
                f"fallback={perception.affective.affect_label}"
            ),
            operation=lambda: self.adapters.run_affective_assessment(graph_state),
            output_summary=lambda result: (
                f"label={result.affective.affect_label} support={result.affective.needs_support} "
                f"source={result.affective.source} confidence={result.affective.confidence}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    def _context_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        updated = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="context",
            input_summary=(
                f"memory={len(graph_state.memory.episodic)} conclusions={len(graph_state.conclusions)} "
                f"goals={len(graph_state.active_goals)} tasks={len(graph_state.active_tasks)} "
                f"milestones={len(graph_state.active_goal_milestones)}"
            ),
            operation=lambda: self.adapters.run_context(graph_state),
            output_summary=lambda result: (
                f"related_goals={len(result.context.related_goals)} "
                f"tags={len(result.context.related_tags)} risk={result.context.risk_level}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    def _motivation_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        perception = graph_state.perception
        context = graph_state.context
        assert perception is not None
        assert context is not None
        updated = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="motivation",
            input_summary=(
                f"intent={perception.intent} risk={context.risk_level} "
                f"preferences={len(graph_state.user_preferences)}"
            ),
            operation=lambda: self.adapters.run_motivation(graph_state),
            output_summary=lambda result: (
                f"mode={result.motivation.mode} importance={result.motivation.importance} "
                f"urgency={result.motivation.urgency} valence={result.motivation.valence}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    def _role_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        perception = graph_state.perception
        assert perception is not None
        updated = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="role",
            input_summary=(
                f"topic={perception.topic} intent={perception.intent} "
                f"preferences={len(graph_state.user_preferences)}"
            ),
            operation=lambda: self.adapters.run_role(graph_state),
            output_summary=lambda result: (
                f"selected={result.role.selected} confidence={result.role.confidence}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    def _planning_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        motivation = graph_state.motivation
        role = graph_state.role
        assert motivation is not None
        assert role is not None
        updated = self._run_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="planning",
            input_summary=(
                f"mode={motivation.mode} role={role.selected} "
                f"goals={len(graph_state.active_goals)} tasks={len(graph_state.active_tasks)}"
            ),
            operation=lambda: self.adapters.run_planning(graph_state),
            output_summary=lambda result: (
                f"steps={len(result.plan.steps)} needs_action={result.plan.needs_action} "
                f"needs_response={result.plan.needs_response}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    async def _expression_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        perception = graph_state.perception
        motivation = graph_state.motivation
        role = graph_state.role
        plan = graph_state.plan
        assert perception is not None
        assert motivation is not None
        assert role is not None
        assert plan is not None
        updated = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="expression",
            input_summary=(
                f"language={perception.language} mode={motivation.mode} role={role.selected} "
                f"needs_response={plan.needs_response}"
            ),
            operation=lambda: self.adapters.run_expression(graph_state),
            output_summary=lambda result: (
                f"tone={result.expression.tone} language={result.expression.language} "
                f"channel={result.expression.channel} message_len={len(result.expression.message)}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    async def _action_node(self, state: dict[str, Any]) -> dict[str, Any]:
        runtime_ctx = self._runtime_ctx(state)
        stage_logger = runtime_ctx["stage_logger"]
        stage_timings_ms = runtime_ctx["stage_timings_ms"]
        graph_state = self._graph_state(state)
        plan = graph_state.plan
        expression = graph_state.expression
        assert plan is not None
        assert expression is not None
        preview_delivery = expression_to_action_delivery(event=graph_state.event, expression=expression)
        updated = await self._run_async_stage(
            stage_logger=stage_logger,
            stage_timings_ms=stage_timings_ms,
            stage="action",
            input_summary=(
                f"needs_action={plan.needs_action} "
                f"channel={preview_delivery.channel} "
                f"has_chat_id={self._present_label(preview_delivery.chat_id)}"
            ),
            operation=lambda: self.adapters.run_action(graph_state),
            output_summary=lambda result: (
                f"status={result.action_result.status} actions={len(result.action_result.actions)}"
            ),
        )
        return {"graph_state": updated, "_runtime": runtime_ctx}

    async def run(
        self,
        *,
        graph_state: GraphRuntimeState,
        stage_logger: RuntimeStageLogger,
        stage_timings_ms: dict[str, int],
        text: str,
        user_profile: dict[str, Any] | None,
    ) -> GraphRuntimeState:
        final_state = await self._graph.ainvoke(
            {
                "graph_state": graph_state,
                "_runtime": {
                    "stage_logger": stage_logger,
                    "stage_timings_ms": stage_timings_ms,
                    "text": text,
                    "user_profile": user_profile,
                },
            }
        )
        graph = final_state.get("graph_state")
        if not isinstance(graph, GraphRuntimeState):
            raise ValueError("langgraph foreground run returned invalid graph_state")
        return graph
