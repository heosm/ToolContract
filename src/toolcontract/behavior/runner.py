# src/toolcontract/behavior/runner.py

import json
from typing import List, Dict, Any
from openai import OpenAI

class BehaviorTestRunner:
    def __init__(self, api_key: str = None):
        """
        OpenAI 클라이언트를 초기화합니다. 
        api_key를 안 넣으면 시스템 환경변수(OPENAI_API_KEY)를 자동으로 찾습니다.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def run_single_test(self, prompt: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        GPT-4o에 프롬프트와 Tool(Function Calling)을 전달하여 어떤 Tool을 고르는지 확인합니다.
        """
        # OpenAI의 tools 파라미터 규격에 맞게 매핑
        # (기존 tools 리스트가 이미 OpenAI 포맷 {"type": "function", "function": {...}} 이라면 변환 생략 가능)
        openai_tools = []
        for t in tools:
            if "type" in t and t["type"] == "function":
                openai_tools.append(t)
            else:
                openai_tools.append({"type": "function", "function": t})

        # LLM 호출
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            tools=openai_tools,
            tool_choice="auto", # LLM이 알아서 적절한 Tool을 선택하도록 함
            temperature=0.0     # 일관된 테스트 결과를 위해 temperature를 낮춤
        )

        message = response.choices[0].message
        
        result = {
            "selected_tool": None,
            "arguments": None,
            "raw_response": message.content,
            "raw_tool_calls": None
        }

        # LLM이 Tool을 선택했는지 확인
        if message.tool_calls:
            # 첫 번째 호출된 Tool 추출
            tool_call = message.tool_calls[0]
            result["selected_tool"] = tool_call.function.name
            result["raw_tool_calls"] = message.tool_calls
            
            # JSON string으로 오는 arguments를 파싱
            try:
                result["arguments"] = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                result["arguments"] = tool_call.function.arguments

        return result

    def run_repeated_test(self, prompt: str, tools: List[Dict[str, Any]], num_repeats: int = 5) -> List[Dict[str, Any]]:
        """
        안정성 검사를 위해 동일한 테스트를 여러 번 실행합니다.
        """
        results = []
        for _ in range(num_repeats):
            results.append(self.run_single_test(prompt, tools))
        return results