import json
from collections import Counter

from toolcontract.behavior.runner import BehaviorTestRunner
from toolcontract.behavior.evaluator import BehaviorEvaluator


def load_behavior_cases(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError(
            "Behavior test file은 JSON 배열이어야 합니다."
        )

    for index, case in enumerate(cases):
        if "prompt" not in case:
            raise ValueError(
                f"{index + 1}번째 case에 prompt가 없습니다."
            )

        if "expected_tool" not in case:
            raise ValueError(
                f"{index + 1}번째 case에 expected_tool이 없습니다."
            )

    return cases


class BehaviorSuiteRunner:
    def __init__(self, provider, model):
        self.runner = BehaviorTestRunner(
            provider=provider,
            model=model,
        )

        self.evaluator = BehaviorEvaluator()

    def run(self, tools, cases):
        case_results = []

        total_runs = 0
        total_passes = 0

        confusion_counter = Counter()

        for index, case in enumerate(cases, start=1):
            name = case.get(
                "name",
                f"Case {index}",
            )

            prompt = case["prompt"]
            expected_tool = case["expected_tool"]
            expected_args = case.get(
                "expected_args",
                {},
            )

            repeats = int(
                case.get("repeats", 3)
            )

            results = self.runner.run_repeated_test(
                prompt=prompt,
                tools=tools,
                num_repeats=repeats,
            )

            metrics = self.evaluator.calculate_metrics(
                results,
                expected_tool,
                expected_args,
            )

            total_runs += metrics["total_runs"]
            total_passes += metrics["pass_count"]

            for result in results:
                actual_tool = (
                    result.get("selected_tool")
                    or "NO_TOOL"
                )

                if actual_tool != expected_tool:
                    confusion_counter[
                        (expected_tool, actual_tool)
                    ] += 1

            case_results.append(
                {
                    "name": name,
                    "prompt": prompt,
                    "expected_tool": expected_tool,
                    "expected_args": expected_args,
                    "results": results,
                    "metrics": metrics,
                }
            )

        accuracy = (
            total_passes / total_runs * 100
            if total_runs
            else 0.0
        )

        confusions = []

        for (
            expected_tool,
            actual_tool,
        ), count in confusion_counter.most_common():

            confusions.append(
                {
                    "expected_tool": expected_tool,
                    "actual_tool": actual_tool,
                    "count": count,
                }
            )

        return {
            "total_cases": len(cases),
            "total_runs": total_runs,
            "pass_count": total_passes,
            "fail_count": total_runs - total_passes,
            "accuracy": round(accuracy, 2),
            "status": (
                "PASS"
                if total_passes == total_runs
                else "FAIL"
            ),
            "cases": case_results,
            "confusions": confusions,
        }