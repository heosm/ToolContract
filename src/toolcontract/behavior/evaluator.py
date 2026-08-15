# src/toolcontract/behavior/evaluator.py

from typing import List, Dict, Any

class BehaviorEvaluator:
    def __init__(self):
        pass

    def check_tool_selection(self, actual_tool: str, expected_tool: str) -> bool:
        """
        LLM이 상황에 맞는 올바른 Tool을 선택했는지 검사합니다.
        """
        return actual_tool == expected_tool

    def check_arguments(self, actual_args: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
        """
        Tool은 맞게 선택했는데 argument를 잘못 생성하는 경우를 검사합니다.
        (예: 필수 파라미터 누락, 타입 불일치, Hallucination 값 등)
        """
        # TODO: JSON Schema 검증 또는 Pydantic 등을 이용한 argument 상세 검사 로직 구현
        return True

    def calculate_metrics(self, test_results: List[Dict[str, Any]], expected_tool: str) -> Dict[str, Any]:
        """
        반복 테스트 결과를 분석하여 정량적인 정확도와 안정성을 계산합니다.
        """
        total_runs = len(test_results)
        if total_runs == 0:
            return {"accuracy": 0.0, "pass_count": 0, "total_runs": 0}

        pass_count = sum(
            1 for res in test_results 
            if self.check_tool_selection(res.get("selected_tool"), expected_tool)
        )

        return {
            "total_runs": total_runs,
            "pass_count": pass_count,
            "accuracy": (pass_count / total_runs) * 100.0,
            "status": "PASS" if pass_count == total_runs else "FAIL"
        }