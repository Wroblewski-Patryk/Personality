from app.utils.goal_task_signals import detect_goal_signal, detect_task_signal


def test_detect_goal_signal_from_explicit_goal_phrase() -> None:
    signal = detect_goal_signal("My goal is to ship the MVP this week.")

    assert signal is not None
    assert signal.name == "ship the MVP this week"
    assert signal.priority == "high"
    assert signal.goal_type == "operational"


def test_detect_task_signal_from_explicit_task_phrase() -> None:
    signal = detect_task_signal("I need to fix the deployment blocker.")

    assert signal is not None
    assert signal.name == "fix the deployment blocker"
    assert signal.priority == "high"
    assert signal.status == "blocked"
