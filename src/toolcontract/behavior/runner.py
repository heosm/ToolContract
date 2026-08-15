# src/toolcontract/behavior/runner.py

from typing import List, Dict, Any

class BehaviorTestRunner:
    def __init__(self, llm_client: Any):
        """
        LLM API 클라이언트(예: OpenAI, Anthropic 등)를 초기화합니다.
        """
        self.llm_client = llm_client

    def run_single_test(self, prompt: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        실제 LLM에 질문을 던지고, 어떤 Tool을 선택했는지 확인합니다.
        """
        # TODO: 실제 LLM 호출 로직 구현 (MCP 연동 또는 직접 API 호출)
        # 응답 예시 포맷 반환
        return {
            "selected_tool": "example_tool_name",
            "arguments": {"arg1": "value1"},
            "raw_response": "..." # 필요 시 LLM의 원본 응답 저장
        }

    def run_repeated_test(self, prompt: str, tools: List[Dict[str, Any]], num_repeats: int = 5) -> List[Dict[str, Any]]:
        """
        같은 종류의 테스트를 여러 번 실행하여 안정성(일관성)을 측정하기 위한 데이터를 수집합니다.
        """
        results = []
        for _ in range(num_repeats):
            result = self.run_single_test(prompt, tools)
            results.append(result)
        return results