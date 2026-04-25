from app.utils.goal_task_signals import detect_goal_signal, detect_task_signal, detect_task_status_signal


def test_detect_goal_signal_from_explicit_goal_phrase() -> None:
    signal = detect_goal_signal("My goal is to ship the MVP this week.")

    assert signal is not None
    assert signal.name == "ship the MVP this week"
    assert signal.priority == "high"
    assert signal.goal_type == "operational"


def test_detect_goal_signal_from_inline_command_phrase() -> None:
    signal = detect_goal_signal("Can you add goal ship the MVP this week and add task fix deployment blocker?")

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


def test_detect_task_signal_from_inline_command_phrase() -> None:
    signal = detect_task_signal("Prosze, dodaj zadanie: naprawic deployment blocker.")

    assert signal is not None
    assert signal.name == "naprawic deployment blocker"
    assert signal.priority == "high"
    assert signal.status == "blocked"


def test_detect_task_signal_from_reminder_phrase() -> None:
    signal = detect_task_signal("Remind me to send the release summary tomorrow.")

    assert signal is not None
    assert signal.name == "send the release summary tomorrow"
    assert signal.priority == "medium"
    assert signal.status == "todo"


def test_detect_task_signal_from_daily_planning_phrase() -> None:
    signal = detect_task_signal("Help me plan tomorrow.")

    assert signal is not None
    assert signal.name == "plan tomorrow"
    assert signal.priority == "medium"
    assert signal.status == "todo"


def test_detect_goal_signal_does_not_match_non_command_mentions() -> None:
    signal = detect_goal_signal("The migration goal is visible in the dashboard.")

    assert signal is None


def test_detect_task_signal_does_not_match_non_command_mentions() -> None:
    signal = detect_task_signal("The task board is synced and stable.")

    assert signal is None


def test_detect_task_status_signal_from_done_phrase() -> None:
    signal = detect_task_status_signal("I fixed the deployment blocker.")

    assert signal is not None
    assert signal.status == "done"
    assert signal.task_hint == "the deployment blocker"
