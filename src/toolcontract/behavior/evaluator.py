from typing import List, Dict, Any


class BehaviorEvaluator:

    def check_tool_selection(
        self,
        actual_tool: str,
        expected_tool: str
    ) -> bool:
        return actual_tool == expected_tool


    def check_arguments(
        self,
        actual_args: Dict[str, Any],
        expected_args: Dict[str, Any]
    ) -> bool:

        if not actual_args or not expected_args:
            return actual_args == expected_args

        for key, expected_value in expected_args.items():

            if key not in actual_args:
                return False

            actual_value = actual_args[key]

            # 숫자/문자열 타입 차이 정규화
            if str(actual_value) != str(expected_value):
                return False

        return True


    def calculate_metrics(
        self,
        test_results: List[Dict[str, Any]],
        expected_tool: str,
        expected_args: Dict[str, Any] = None
    ) -> Dict[str, Any]:

        total_runs = len(test_results)

        if total_runs == 0:
            return {
                "accuracy": 0.0,
                "pass_count": 0,
                "total_runs": 0
            }

        pass_count = 0

        for res in test_results:

            tool_passed = self.check_tool_selection(
                res.get("selected_tool"),
                expected_tool
            )

            args_passed = True

            if expected_args:
                args_passed = self.check_arguments(
                    res.get("arguments") or {},
                    expected_args
                )

            if tool_passed and args_passed:
                pass_count += 1

        return {
            "total_runs": total_runs,
            "pass_count": pass_count,
            "accuracy": (pass_count / total_runs) * 100.0,
            "status": "PASS" if pass_count == total_runs else "FAIL"
        }