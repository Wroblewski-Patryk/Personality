def goal_history_signal(goal_progress_history: list[dict]) -> str:
    if len(goal_progress_history) < 2:
        return ""

    ordered = list(reversed(goal_progress_history))
    scores: list[float] = []
    for item in ordered:
        try:
            scores.append(float(item.get("score", 0.0)))
        except (TypeError, ValueError):
            continue

    if len(scores) < 2:
        return ""

    delta = round(scores[-1] - scores[0], 2)
    span = round(max(scores) - min(scores), 2)
    if delta <= -0.2:
        return "regression"
    if delta >= 0.2:
        return "lift"
    if span >= 0.3:
        return "volatile"
    return ""


def goal_milestone_arc_signal(
    goal_milestone_history: list[dict],
    *,
    current_phase: str = "",
    current_risk: str = "",
    transition: str = "",
    require_transition_for_reentry: bool = False,
) -> str:
    states = _compact_milestone_states(
        goal_milestone_history=goal_milestone_history,
        current_phase=current_phase,
        current_risk=current_risk,
    )
    if len(states) < 2:
        return ""

    previous_phase, previous_risk = states[-2]
    current_phase_value, current_risk_value = states[-1]
    had_completion_before = any(phase == "completion_window" for phase, _ in states[:-1])
    had_recovery_before = any(phase == "recovery_phase" for phase, _ in states[:-1])
    phase_changes = sum(
        1
        for index in range(1, len(states))
        if states[index][0] and states[index - 1][0] and states[index][0] != states[index - 1][0]
    )
    distinct_phases = {phase for phase, _ in states if phase}

    reentry_condition = (
        current_phase_value == "completion_window"
        and had_completion_before
        and had_recovery_before
        and previous_phase != "completion_window"
    )
    if require_transition_for_reentry:
        reentry_condition = reentry_condition and transition == "entered_completion_window"
    if reentry_condition:
        return "reentered_completion_window"
    if current_phase_value == "recovery_phase" and had_completion_before:
        return "recovery_backslide"
    if len(distinct_phases) >= 3 and phase_changes >= 3:
        return "milestone_whiplash"
    if current_phase_value == "completion_window" and previous_phase == "completion_window":
        return "steady_closure"
    if current_phase_value == "completion_window" and (
        previous_phase != "completion_window"
        or (previous_risk in {"watch", "stabilizing", "on_track"} and current_risk_value == "ready_to_close")
    ):
        return "closure_momentum"
    return ""


def _compact_milestone_states(
    *,
    goal_milestone_history: list[dict],
    current_phase: str,
    current_risk: str,
) -> list[tuple[str, str]]:
    ordered = list(reversed(goal_milestone_history))
    states: list[tuple[str, str]] = []
    for item in ordered:
        pair = (
            str(item.get("phase", "")).strip().lower(),
            str(item.get("risk_level", "")).strip().lower(),
        )
        if not pair[0] and not pair[1]:
            continue
        if not states or states[-1] != pair:
            states.append(pair)

    current_pair = (
        str(current_phase).strip().lower(),
        str(current_risk).strip().lower(),
    )
    if current_pair[0] or current_pair[1]:
        if not states or states[-1] != current_pair:
            states.append(current_pair)
    return states
