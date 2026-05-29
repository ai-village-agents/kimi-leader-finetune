from examples.best_coordination_demo import build_demo_tracker
from ai_village_toolkit import AgentStatus


def test_demo_tracker_summary_and_assignment():
    tracker = build_demo_tracker()
    summary = tracker.summary()
    assert summary["room"] == "#best"
    assert summary["agents"]["GPT-5.5"] == AgentStatus.WORKING.name
    assert summary["active_assignments"] == 1
    assert tracker.assignments_for("GPT-5.5")[0].task_id == "history-helper-review"
