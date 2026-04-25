from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from inspect import isawaitable
from typing import Any, Literal, TypeAlias

from pydantic import BaseModel

BehaviorStatus = Literal["pass", "fail", "skip"]


class BehaviorScenarioResult(BaseModel):
    test_id: str
    status: BehaviorStatus
    reason: str
    trace_id: str
    notes: str = ""


@dataclass(slots=True)
class BehaviorScenarioCheck:
    passed: bool
    reason: str
    trace_id: str
    notes: str = ""
    skip: bool = False


BehaviorScenarioRunner: TypeAlias = Callable[[], BehaviorScenarioCheck | Awaitable[BehaviorScenarioCheck]]


@dataclass(slots=True)
class BehaviorScenarioDefinition:
    test_id: str
    run: BehaviorScenarioRunner


def build_behavior_result(*, test_id: str, check: BehaviorScenarioCheck) -> BehaviorScenarioResult:
    if check.skip:
        status: BehaviorStatus = "skip"
    elif check.passed:
        status = "pass"
    else:
        status = "fail"
    return BehaviorScenarioResult(
        test_id=test_id,
        status=status,
        reason=check.reason,
        trace_id=check.trace_id,
        notes=check.notes,
    )


async def execute_behavior_scenarios(
    scenarios: Sequence[BehaviorScenarioDefinition],
) -> list[BehaviorScenarioResult]:
    results: list[BehaviorScenarioResult] = []
    for scenario in scenarios:
        try:
            check = scenario.run()
            if isawaitable(check):
                check = await check
        except Exception as exc:  # pragma: no cover - defensive behavior harness boundary
            results.append(
                BehaviorScenarioResult(
                    test_id=scenario.test_id,
                    status="fail",
                    reason=f"scenario_execution_error:{type(exc).__name__}",
                    trace_id="-",
                    notes=str(exc),
                )
            )
            continue
        results.append(build_behavior_result(test_id=scenario.test_id, check=check))
    return results


def behavior_results_as_jsonable(results: Sequence[BehaviorScenarioResult]) -> list[dict[str, Any]]:
    return [result.model_dump(mode="json") for result in results]
