from collections.abc import Callable, Sequence

from app.utils.progress_signals import goal_milestone_arc_signal as shared_goal_milestone_arc_signal


def derive_goal_execution_state(
    *,
    recent_memory: Sequence[dict],
    active_goals: Sequence[dict],
    active_tasks: Sequence[dict],
    task_done_updates: int,
    task_in_progress_updates: int,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> dict | None:
    if not active_goals:
        return None

    blocked_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "blocked"
    ]
    in_progress_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "in_progress"
    ]
    remaining_active_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() in {"todo", "in_progress"}
    ]

    if blocked_tasks:
        return {
            "kind": "goal_execution_state",
            "content": "blocked",
            "confidence": 0.82,
            "source": "background_reflection",
        }

    if task_done_updates >= 1 and remaining_active_tasks:
        return {
            "kind": "goal_execution_state",
            "content": "recovering",
            "confidence": 0.77,
            "source": "background_reflection",
        }

    if in_progress_tasks or task_in_progress_updates >= 1:
        return {
            "kind": "goal_execution_state",
            "content": "advancing",
            "confidence": 0.75,
            "source": "background_reflection",
        }

    if task_done_updates >= 1:
        return {
            "kind": "goal_execution_state",
            "content": "progressing",
            "confidence": 0.76,
            "source": "background_reflection",
        }

    if goal_stagnation_signal_count(recent_memory, extract_memory_fields=extract_memory_fields) >= 3:
        return {
            "kind": "goal_execution_state",
            "content": "stagnating",
            "confidence": 0.72,
            "source": "background_reflection",
        }

    return None


def derive_goal_progress_score(
    *,
    active_goals: Sequence[dict],
    active_tasks: Sequence[dict],
    task_done_updates: int,
) -> dict | None:
    if not active_goals:
        return None

    signal_count = len(active_tasks) + task_done_updates
    if signal_count <= 0:
        return None

    weighted_progress = float(task_done_updates)
    for task in active_tasks:
        status = str(task.get("status", "")).strip().lower()
        weighted_progress += {
            "blocked": 0.1,
            "todo": 0.3,
            "in_progress": 0.65,
        }.get(status, 0.0)

    score = min(0.99, max(0.0, round(weighted_progress / signal_count, 2)))
    confidence = 0.74 if signal_count >= 2 else 0.7
    return {
        "kind": "goal_progress_score",
        "content": f"{score:.2f}",
        "confidence": confidence,
        "source": "background_reflection",
    }


def derive_goal_progress_trend(
    *,
    current_goal_progress_score: dict | None,
    previous_goal_progress_score: float | None,
    coerce_progress_score: Callable[[object], float | None],
) -> dict | None:
    current_score = coerce_progress_score(
        current_goal_progress_score.get("content") if current_goal_progress_score else None
    )
    if current_score is None or previous_goal_progress_score is None:
        return None

    delta = round(current_score - previous_goal_progress_score, 2)
    if delta >= 0.12:
        return {
            "kind": "goal_progress_trend",
            "content": "improving",
            "confidence": 0.73,
            "source": "background_reflection",
        }
    if delta <= -0.12:
        return {
            "kind": "goal_progress_trend",
            "content": "slipping",
            "confidence": 0.75,
            "source": "background_reflection",
        }
    if abs(delta) <= 0.05 and current_score > 0.0:
        return {
            "kind": "goal_progress_trend",
            "content": "steady",
            "confidence": 0.7,
            "source": "background_reflection",
        }
    return None


def derive_goal_progress_arc(
    *,
    recent_goal_progress: Sequence[dict],
    current_goal_progress_score: dict | None,
    goal_execution_state: dict | None,
    goal_progress_trend: dict | None,
    coerce_progress_score: Callable[[object], float | None],
) -> dict | None:
    current_score = coerce_progress_score(
        current_goal_progress_score.get("content") if current_goal_progress_score else None
    )
    if current_score is None:
        return None

    ordered_history = list(reversed(recent_goal_progress))
    scores: list[float] = []
    states: list[str] = []
    for item in ordered_history:
        score = coerce_progress_score(item.get("score"))
        if score is None:
            continue
        scores.append(score)
        states.append(str(item.get("execution_state", "")).strip().lower())

    scores.append(current_score)
    states.append(str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else "")

    if len(scores) < 2:
        return None

    start = round(scores[0], 2)
    end = round(scores[-1], 2)
    delta = round(end - start, 2)
    span = round(max(scores) - min(scores), 2)
    trend = str(goal_progress_trend.get("content", "")).strip().lower() if goal_progress_trend is not None else ""
    has_recovery_state = any(state in {"blocked", "recovering"} for state in states)

    if has_recovery_state and trend == "improving" and end >= 0.5:
        return {
            "kind": "goal_progress_arc",
            "content": "recovery_gaining_traction",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    if trend == "improving" and delta >= 0.35 and end >= 0.75:
        return {
            "kind": "goal_progress_arc",
            "content": "breakthrough_momentum",
            "confidence": 0.77,
            "source": "background_reflection",
        }
    if span >= 0.35 and abs(delta) < 0.15:
        return {
            "kind": "goal_progress_arc",
            "content": "unstable_progress",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    if trend == "slipping" and delta <= -0.2 and end <= 0.35:
        return {
            "kind": "goal_progress_arc",
            "content": "falling_behind",
            "confidence": 0.78,
            "source": "background_reflection",
        }
    if trend == "steady" and start >= 0.45 and end >= 0.45:
        return {
            "kind": "goal_progress_arc",
            "content": "holding_pattern",
            "confidence": 0.71,
            "source": "background_reflection",
        }
    return None


def derive_goal_milestone_transition(
    *,
    current_goal_progress_score: dict | None,
    previous_goal_progress_score: float | None,
    coerce_progress_score: Callable[[object], float | None],
) -> dict | None:
    current_score = coerce_progress_score(
        current_goal_progress_score.get("content") if current_goal_progress_score else None
    )
    if current_score is None or previous_goal_progress_score is None:
        return None

    previous_score = round(previous_goal_progress_score, 2)
    current_score = round(current_score, 2)

    if previous_score >= 0.75 and current_score < 0.75:
        return {
            "kind": "goal_milestone_transition",
            "content": "slipped_from_completion_window",
            "confidence": 0.78,
            "source": "background_reflection",
        }
    if previous_score < 0.75 and current_score >= 0.75:
        return {
            "kind": "goal_milestone_transition",
            "content": "entered_completion_window",
            "confidence": 0.77,
            "source": "background_reflection",
        }
    if previous_score >= 0.35 and current_score < 0.35:
        return {
            "kind": "goal_milestone_transition",
            "content": "dropped_back_to_early_stage",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    if previous_score < 0.35 and current_score >= 0.35:
        return {
            "kind": "goal_milestone_transition",
            "content": "entered_execution_phase",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    return None


def derive_goal_milestone_state(
    *,
    has_active_goal: bool,
    current_goal_progress_score: dict | None,
    goal_execution_state: dict | None,
    goal_progress_arc: dict | None,
    coerce_progress_score: Callable[[object], float | None],
) -> dict | None:
    if not has_active_goal:
        return None
    current_score = coerce_progress_score(
        current_goal_progress_score.get("content") if current_goal_progress_score else None
    )
    if current_score is None:
        return {
            "kind": "goal_milestone_state",
            "content": "early_stage",
            "confidence": 0.7,
            "source": "background_reflection",
        }
    if current_score <= 0.0:
        return None

    execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
    progress_arc = str(goal_progress_arc.get("content", "")).strip().lower() if goal_progress_arc is not None else ""

    if current_score >= 0.75:
        return {
            "kind": "goal_milestone_state",
            "content": "completion_window",
            "confidence": 0.8,
            "source": "background_reflection",
        }
    if execution_state == "recovering" or progress_arc == "recovery_gaining_traction":
        return {
            "kind": "goal_milestone_state",
            "content": "recovery_phase",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    if current_score >= 0.35:
        return {
            "kind": "goal_milestone_state",
            "content": "execution_phase",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    return {
        "kind": "goal_milestone_state",
        "content": "early_stage",
        "confidence": 0.72,
        "source": "background_reflection",
    }


def derive_goal_milestone_arc(
    *,
    recent_goal_milestone_history: Sequence[dict],
    goal_milestone_state: dict | None,
    goal_milestone_transition: dict | None,
) -> dict | None:
    current_phase = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    if not current_phase:
        return None

    transition = (
        str(goal_milestone_transition.get("content", "")).strip().lower()
        if goal_milestone_transition is not None
        else ""
    )
    content = shared_goal_milestone_arc_signal(
        list(recent_goal_milestone_history),
        current_phase=current_phase,
        transition=transition,
        require_transition_for_reentry=True,
    )
    if not content:
        return None

    confidence = {
        "reentered_completion_window": 0.79,
        "recovery_backslide": 0.78,
        "milestone_whiplash": 0.77,
        "closure_momentum": 0.76,
        "steady_closure": 0.75,
    }.get(content, 0.74)
    return {
        "kind": "goal_milestone_arc",
        "content": content,
        "confidence": confidence,
        "source": "background_reflection",
    }


def derive_goal_milestone_pressure(
    *,
    recent_goal_milestone_history: Sequence[dict],
    goal_milestone_state: dict | None,
    goal_milestone_arc: dict | None,
    goal_milestone_transition: dict | None,
) -> dict | None:
    current_phase = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    latest_history_phase = ""
    if recent_goal_milestone_history:
        latest_history_phase = str(recent_goal_milestone_history[0].get("phase", "")).strip().lower()
    if (not current_phase or current_phase == "early_stage") and latest_history_phase:
        current_phase = latest_history_phase
    if not current_phase:
        return None

    milestone_arc = str(goal_milestone_arc.get("content", "")).strip().lower() if goal_milestone_arc is not None else ""
    transition = (
        str(goal_milestone_transition.get("content", "")).strip().lower()
        if goal_milestone_transition is not None
        else ""
    )

    ordered_history = list(reversed(recent_goal_milestone_history))
    consecutive_same_phase = 1
    found_current_phase = False
    for item in reversed(ordered_history):
        phase = str(item.get("phase", "")).strip().lower()
        if phase != current_phase:
            if found_current_phase:
                break
            continue
        found_current_phase = True
        consecutive_same_phase += 1

    if current_phase == "completion_window":
        if consecutive_same_phase >= 4:
            return {
                "kind": "goal_milestone_pressure",
                "content": "lingering_completion",
                "confidence": 0.8,
                "source": "background_reflection",
            }
        if milestone_arc in {"closure_momentum", "reentered_completion_window"} or transition == "entered_completion_window":
            return {
                "kind": "goal_milestone_pressure",
                "content": "building_closure_pressure",
                "confidence": 0.74,
                "source": "background_reflection",
            }
        return None

    if current_phase == "recovery_phase" and consecutive_same_phase >= 3:
        return {
            "kind": "goal_milestone_pressure",
            "content": "dragging_recovery",
            "confidence": 0.78,
            "source": "background_reflection",
        }

    if current_phase == "execution_phase" and consecutive_same_phase >= 4:
        return {
            "kind": "goal_milestone_pressure",
            "content": "stale_execution",
            "confidence": 0.75,
            "source": "background_reflection",
        }

    if current_phase == "early_stage" and consecutive_same_phase >= 4:
        return {
            "kind": "goal_milestone_pressure",
            "content": "lingering_setup",
            "confidence": 0.74,
            "source": "background_reflection",
        }

    return None


def derive_goal_milestone_dependency_state(
    *,
    active_tasks: Sequence[dict],
    goal_milestone_state: dict | None,
    goal_execution_state: dict | None,
) -> dict | None:
    milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
    blocked_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "blocked"
    ]
    remaining_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() in {"todo", "in_progress", "blocked"}
    ]

    if blocked_tasks or execution_state == "blocked":
        return {
            "kind": "goal_milestone_dependency_state",
            "content": "blocked_dependency",
            "confidence": 0.83,
            "source": "background_reflection",
        }
    if len(remaining_tasks) >= 2:
        return {
            "kind": "goal_milestone_dependency_state",
            "content": "multi_step_dependency",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    if len(remaining_tasks) == 1:
        return {
            "kind": "goal_milestone_dependency_state",
            "content": "single_step_dependency",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    if milestone_state == "completion_window":
        return {
            "kind": "goal_milestone_dependency_state",
            "content": "clear_to_close",
            "confidence": 0.79,
            "source": "background_reflection",
        }
    return None


def derive_goal_milestone_due_state(
    *,
    goal_milestone_state: dict | None,
    goal_milestone_pressure: dict | None,
    goal_milestone_dependency_state: dict | None,
    goal_completion_criteria: dict | None,
) -> dict | None:
    milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    pressure = str(goal_milestone_pressure.get("content", "")).strip().lower() if goal_milestone_pressure is not None else ""
    dependency_state = (
        str(goal_milestone_dependency_state.get("content", "")).strip().lower()
        if goal_milestone_dependency_state is not None
        else ""
    )
    completion_criteria = (
        str(goal_completion_criteria.get("content", "")).strip().lower()
        if goal_completion_criteria is not None
        else ""
    )

    if milestone_state == "completion_window":
        if dependency_state == "clear_to_close" or completion_criteria == "confirm_goal_completion":
            return {
                "kind": "goal_milestone_due_state",
                "content": "closure_due_now",
                "confidence": 0.82,
                "source": "background_reflection",
            }
        if dependency_state in {"blocked_dependency", "single_step_dependency", "multi_step_dependency"}:
            return {
                "kind": "goal_milestone_due_state",
                "content": "dependency_due_next",
                "confidence": 0.79,
                "source": "background_reflection",
            }
        return None

    if milestone_state == "recovery_phase" and pressure == "dragging_recovery":
        return {
            "kind": "goal_milestone_due_state",
            "content": "recovery_due_attention",
            "confidence": 0.77,
            "source": "background_reflection",
        }

    if milestone_state == "execution_phase" and pressure == "stale_execution":
        return {
            "kind": "goal_milestone_due_state",
            "content": "execution_due_attention",
            "confidence": 0.75,
            "source": "background_reflection",
        }

    if milestone_state == "early_stage" and pressure == "lingering_setup":
        return {
            "kind": "goal_milestone_due_state",
            "content": "setup_due_start",
            "confidence": 0.74,
            "source": "background_reflection",
        }

    return None


def derive_goal_milestone_due_window(
    *,
    goal_milestone_due_state: dict | None,
    goal_milestone_pressure: dict | None,
    goal_milestone_arc: dict | None,
    goal_milestone_transition: dict | None,
) -> dict | None:
    due_state = str(goal_milestone_due_state.get("content", "")).strip().lower() if goal_milestone_due_state is not None else ""
    pressure = str(goal_milestone_pressure.get("content", "")).strip().lower() if goal_milestone_pressure is not None else ""
    milestone_arc = str(goal_milestone_arc.get("content", "")).strip().lower() if goal_milestone_arc is not None else ""
    transition = (
        str(goal_milestone_transition.get("content", "")).strip().lower()
        if goal_milestone_transition is not None
        else ""
    )

    if not due_state:
        return None
    if milestone_arc == "reentered_completion_window":
        return {
            "kind": "goal_milestone_due_window",
            "content": "reopened_due_window",
            "confidence": 0.8,
            "source": "background_reflection",
        }
    if pressure in {"lingering_completion", "dragging_recovery", "stale_execution", "lingering_setup"}:
        return {
            "kind": "goal_milestone_due_window",
            "content": "overdue_due_window",
            "confidence": 0.82,
            "source": "background_reflection",
        }
    if transition == "entered_completion_window" or pressure == "building_closure_pressure":
        return {
            "kind": "goal_milestone_due_window",
            "content": "fresh_due_window",
            "confidence": 0.76,
            "source": "background_reflection",
        }
    return {
        "kind": "goal_milestone_due_window",
        "content": "active_due_window",
        "confidence": 0.73,
        "source": "background_reflection",
    }


def derive_goal_milestone_risk(
    *,
    active_tasks: Sequence[dict],
    goal_execution_state: dict | None,
    goal_progress_arc: dict | None,
    goal_milestone_state: dict | None,
    goal_milestone_transition: dict | None,
) -> dict | None:
    execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
    progress_arc = str(goal_progress_arc.get("content", "")).strip().lower() if goal_progress_arc is not None else ""
    milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    milestone_transition = (
        str(goal_milestone_transition.get("content", "")).strip().lower()
        if goal_milestone_transition is not None
        else ""
    )
    blocked_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "blocked"
    ]

    if blocked_tasks or execution_state == "blocked" or progress_arc == "falling_behind":
        return {
            "kind": "goal_milestone_risk",
            "content": "at_risk",
            "confidence": 0.81,
            "source": "background_reflection",
        }
    if milestone_transition == "slipped_from_completion_window" or progress_arc == "unstable_progress":
        return {
            "kind": "goal_milestone_risk",
            "content": "watch",
            "confidence": 0.75,
            "source": "background_reflection",
        }
    if milestone_state == "completion_window":
        return {
            "kind": "goal_milestone_risk",
            "content": "ready_to_close",
            "confidence": 0.79,
            "source": "background_reflection",
        }
    if milestone_state == "recovery_phase" or progress_arc == "recovery_gaining_traction":
        return {
            "kind": "goal_milestone_risk",
            "content": "stabilizing",
            "confidence": 0.74,
            "source": "background_reflection",
        }
    if milestone_state in {"execution_phase", "early_stage"} or execution_state in {"advancing", "progressing"}:
        return {
            "kind": "goal_milestone_risk",
            "content": "on_track",
            "confidence": 0.71,
            "source": "background_reflection",
        }
    return None


def derive_goal_completion_criteria(
    *,
    active_tasks: Sequence[dict],
    goal_execution_state: dict | None,
    goal_milestone_state: dict | None,
    goal_milestone_risk: dict | None,
) -> dict | None:
    milestone_state = str(goal_milestone_state.get("content", "")).strip().lower() if goal_milestone_state is not None else ""
    execution_state = str(goal_execution_state.get("content", "")).strip().lower() if goal_execution_state is not None else ""
    milestone_risk = str(goal_milestone_risk.get("content", "")).strip().lower() if goal_milestone_risk is not None else ""
    blocked_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "blocked"
    ]
    in_progress_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "in_progress"
    ]
    todo_tasks = [
        task
        for task in active_tasks
        if str(task.get("status", "")).strip().lower() == "todo"
    ]

    if milestone_state == "completion_window":
        if blocked_tasks:
            return {
                "kind": "goal_completion_criteria",
                "content": "resolve_remaining_blocker",
                "confidence": 0.82,
                "source": "background_reflection",
            }
        if in_progress_tasks or todo_tasks:
            return {
                "kind": "goal_completion_criteria",
                "content": "finish_remaining_active_work",
                "confidence": 0.8,
                "source": "background_reflection",
            }
        return {
            "kind": "goal_completion_criteria",
            "content": "confirm_goal_completion",
            "confidence": 0.79,
            "source": "background_reflection",
        }

    if blocked_tasks:
        return {
            "kind": "goal_completion_criteria",
            "content": "resolve_remaining_blocker",
            "confidence": 0.82,
            "source": "background_reflection",
        }

    if milestone_state == "recovery_phase" or execution_state == "recovering" or milestone_risk == "stabilizing":
        return {
            "kind": "goal_completion_criteria",
            "content": "stabilize_remaining_work",
            "confidence": 0.76,
            "source": "background_reflection",
        }

    if milestone_state == "early_stage":
        return {
            "kind": "goal_completion_criteria",
            "content": "define_first_execution_step",
            "confidence": 0.72,
            "source": "background_reflection",
        }

    if milestone_state == "execution_phase":
        return {
            "kind": "goal_completion_criteria",
            "content": "advance_next_task",
            "confidence": 0.74,
            "source": "background_reflection",
        }

    return None


def goal_stagnation_signal_count(
    recent_memory: Sequence[dict],
    *,
    extract_memory_fields: Callable[[dict], dict[str, str]],
) -> int:
    planning_heavy_steps = {
        "align_with_active_goal",
        "break_down_problem",
        "highlight_next_step",
        "offer_guidance",
        "favor_guided_walkthrough",
        "review_context",
    }
    execution_steps = {
        "identify_requested_change",
        "propose_execution_step",
        "advance_active_task",
        "unblock_active_task",
        "recover_goal_progress",
        "preserve_goal_momentum",
        "favor_concrete_next_step",
    }

    stagnation_signals = 0
    for memory_item in recent_memory:
        fields = extract_memory_fields(memory_item)
        if fields.get("action", "").strip().lower() != "success":
            continue
        if fields.get("task_status_update", "").strip():
            continue
        if fields.get("task_update", "").strip():
            continue

        plan_steps = {
            step.strip().lower()
            for step in fields.get("plan_steps", "").split(",")
            if step.strip()
        }
        if "align_with_active_goal" not in plan_steps:
            continue
        if plan_steps.intersection(execution_steps):
            continue
        if not plan_steps.intersection(planning_heavy_steps):
            continue
        stagnation_signals += 1

    return stagnation_signals
