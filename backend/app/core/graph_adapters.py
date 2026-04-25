from typing import Any

from app.affective.assessor import AffectiveAssessor
from app.agents.context import ContextAgent
from app.agents.perception import PerceptionAgent
from app.agents.planning import PlanningAgent
from app.agents.role import RoleAgent
from app.core.action import ActionExecutor
from app.core.graph_state import GraphRuntimeState, expression_to_action_delivery
from app.expression.generator import ExpressionAgent
from app.motivation.engine import MotivationEngine


class GraphStageAdapters:
    """Graph-compatible wrappers around existing stage modules."""

    def __init__(
        self,
        *,
        perception_agent: PerceptionAgent,
        context_agent: ContextAgent,
        motivation_engine: MotivationEngine,
        role_agent: RoleAgent,
        planning_agent: PlanningAgent,
        expression_agent: ExpressionAgent,
        action_executor: ActionExecutor,
        affective_assessor: AffectiveAssessor | None = None,
    ):
        self.perception_agent = perception_agent
        self.context_agent = context_agent
        self.motivation_engine = motivation_engine
        self.role_agent = role_agent
        self.planning_agent = planning_agent
        self.expression_agent = expression_agent
        self.action_executor = action_executor
        self.affective_assessor = affective_assessor or AffectiveAssessor()

    def _operational(self, state: GraphRuntimeState) -> dict[str, Any]:
        return dict(state.memory.operational)

    def _require(self, state: GraphRuntimeState, *field_names: str) -> None:
        missing = [name for name in field_names if getattr(state, name) is None]
        if missing:
            raise ValueError(f"missing graph state fields: {', '.join(missing)}")

    def run_perception(self, state: GraphRuntimeState) -> GraphRuntimeState:
        operational = self._operational(state)
        recent_memory = list(state.memory.episodic)
        user_profile = operational.get("user_profile")
        perception = self.perception_agent.run(
            state.event,
            recent_memory=recent_memory,
            user_profile=user_profile if isinstance(user_profile, dict) else None,
        )
        return state.model_copy(update={"perception": perception, "affective_input": perception.affective})

    async def run_affective_assessment(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "perception")
        perception = state.perception
        assert perception is not None
        user_text = str(state.event.payload.get("text", "")).strip()
        affective = await self.affective_assessor.assess(
            user_text=user_text,
            response_language=perception.language,
            fallback=perception.affective,
        )
        updated_perception = perception.model_copy(update={"affective": affective})
        return state.model_copy(
            update={
                "perception": updated_perception,
                "affective": affective,
                "affective_input": state.affective_input or perception.affective,
            }
        )

    def run_context(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "identity", "perception")
        identity = state.identity
        perception = state.perception
        assert identity is not None
        assert perception is not None
        conclusions = list(state.conclusions or state.memory.semantic)
        context = self.context_agent.run(
            event=state.event,
            perception=perception,
            recent_memory=list(state.memory.episodic),
            conclusions=conclusions,
            relations=list(state.relations),
            identity=identity,
            active_goals=list(state.active_goals),
            active_tasks=list(state.active_tasks),
            active_goal_milestones=list(state.active_goal_milestones),
            goal_milestone_history=list(state.goal_milestone_history),
            goal_progress_history=list(state.goal_progress_history),
        )
        return state.model_copy(update={"context": context})

    def run_motivation(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "context", "perception")
        context = state.context
        perception = state.perception
        assert context is not None
        assert perception is not None
        operational = self._operational(state)
        user_preferences = state.user_preferences or operational.get("user_preferences") or {}
        theta = state.theta if state.theta is not None else operational.get("user_theta")
        motivation = self.motivation_engine.run(
            event=state.event,
            context=context,
            perception=perception,
            user_preferences=dict(user_preferences),
            theta=theta if isinstance(theta, dict) else None,
            relations=list(state.relations),
            active_goals=list(state.active_goals),
            active_tasks=list(state.active_tasks),
            goal_milestone_history=list(state.goal_milestone_history),
            goal_progress_history=list(state.goal_progress_history),
        )
        return state.model_copy(update={"motivation": motivation})

    def run_role(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "perception", "context")
        perception = state.perception
        context = state.context
        assert perception is not None
        assert context is not None
        operational = self._operational(state)
        user_preferences = state.user_preferences or operational.get("user_preferences") or {}
        theta = state.theta if state.theta is not None else operational.get("user_theta")
        role = self.role_agent.run(
            event=state.event,
            perception=perception,
            context=context,
            user_preferences=dict(user_preferences),
            relations=list(state.relations),
            theta=theta if isinstance(theta, dict) else None,
        )
        return state.model_copy(update={"role": role})

    def run_planning(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "context", "motivation", "role")
        context = state.context
        motivation = state.motivation
        role = state.role
        assert context is not None
        assert motivation is not None
        assert role is not None
        operational = self._operational(state)
        user_preferences = state.user_preferences or operational.get("user_preferences") or {}
        theta = state.theta if state.theta is not None else operational.get("user_theta")
        subconscious_proposals: list[dict] = []
        for proposal in state.subconscious_proposals:
            if hasattr(proposal, "model_dump"):
                subconscious_proposals.append(proposal.model_dump(mode="python"))  # type: ignore[call-arg]
                continue
            if isinstance(proposal, dict):
                subconscious_proposals.append(dict(proposal))
        plan = self.planning_agent.run(
            event=state.event,
            context=context,
            motivation=motivation,
            role=role,
            user_preferences=dict(user_preferences),
            relations=list(state.relations),
            theta=theta if isinstance(theta, dict) else None,
            active_goals=list(state.active_goals),
            active_tasks=list(state.active_tasks),
            active_planned_work=list(state.active_planned_work),
            active_goal_milestones=list(state.active_goal_milestones),
            goal_milestone_history=list(state.goal_milestone_history),
            goal_progress_history=list(state.goal_progress_history),
            subconscious_proposals=subconscious_proposals,
        )
        return state.model_copy(update={"plan": plan})

    async def run_expression(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "perception", "context", "plan", "role", "motivation", "identity")
        perception = state.perception
        context = state.context
        plan = state.plan
        role = state.role
        motivation = state.motivation
        identity = state.identity
        assert perception is not None
        assert context is not None
        assert plan is not None
        assert role is not None
        assert motivation is not None
        assert identity is not None
        operational = self._operational(state)
        user_preferences = state.user_preferences or operational.get("user_preferences") or {}
        theta = state.theta if state.theta is not None else operational.get("user_theta")
        expression = await self.expression_agent.run(
            event=state.event,
            perception=perception,
            context=context,
            plan=plan,
            role=role,
            motivation=motivation,
            identity=identity,
            user_preferences=dict(user_preferences),
            theta=theta if isinstance(theta, dict) else None,
            relations=list(state.relations),
        )
        delivery = expression_to_action_delivery(
            event=state.event,
            expression=expression,
            plan=plan,
        )
        return state.model_copy(update={"expression": expression, "action_delivery": delivery})

    async def run_action(self, state: GraphRuntimeState) -> GraphRuntimeState:
        self._require(state, "plan", "action_delivery")
        plan = state.plan
        delivery = state.action_delivery
        assert plan is not None
        assert delivery is not None
        action_result = await self.action_executor.execute(plan=plan, delivery=delivery)
        return state.model_copy(update={"action_delivery": delivery, "action_result": action_result})
