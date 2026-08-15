# src/toolcontract/behavior/runner.py

import os
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI


# 프로젝트 루트의 .env 파일 로드
load_dotenv()


class BehaviorTestRunner:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY를 찾을 수 없습니다. "
                "프로젝트 루트의 .env 파일을 확인하세요."
            )

        # Groq는 OpenAI 호환 API를 제공하므로 OpenAI 클라이언트 사용
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

        # Tool Calling 지원 모델
        self.model = "llama-3.3-70b-versatile"

    def _convert_tools(
        self,
        tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        ToolContract의 MCP 스타일 Tool 정의를
        OpenAI/Groq Tool Calling 형식으로 변환합니다.

        ToolContract:
        {
            "name": "...",
            "description": "...",
            "inputSchema": {...}
        }

        OpenAI/Groq:
        {
            "type": "function",
            "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
            }
        }
        """

        openai_tools = []

        for tool in tools:

            # 이미 OpenAI Tool Calling 형식이라면 그대로 사용
            if (
                tool.get("type") == "function"
                and "function" in tool
            ):
                openai_tools.append(tool)
                continue

            input_schema = tool.get(
                "inputSchema",
                {
                    "type": "object",
                    "properties": {}
                }
            )

            function_definition = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": input_schema
            }

            openai_tools.append({
                "type": "function",
                "function": function_definition
            })

        return openai_tools

    def run_single_test(
        self,
        prompt: str,
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        하나의 프롬프트를 LLM에 전달하고
        어떤 Tool을 선택했는지 확인합니다.
        """

        # ToolContract 형식 → Groq/OpenAI 형식
        openai_tools = self._convert_tools(tools)

        # LLM 호출
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=openai_tools,
            tool_choice="auto",
            temperature=0.0
        )

        message = response.choices[0].message

        result = {
            "selected_tool": None,
            "arguments": None,
            "raw_response": message.content,
            "raw_tool_calls": None
        }

        # LLM이 Tool을 호출한 경우
        if message.tool_calls:
            tool_call = message.tool_calls[0]

            result["selected_tool"] = tool_call.function.name
            result["raw_tool_calls"] = message.tool_calls

            # arguments는 JSON 문자열로 전달됨
            try:
                result["arguments"] = json.loads(
                    tool_call.function.arguments
                )
            except (json.JSONDecodeError, TypeError):
                result["arguments"] = tool_call.function.arguments

        return result

    def run_repeated_test(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        num_repeats: int = 5
    ) -> List[Dict[str, Any]]:
        """
        동일한 프롬프트를 여러 번 실행하여
        Tool 선택의 안정성을 검사합니다.
        """

        results = []

        for _ in range(num_repeats):
            result = self.run_single_test(
                prompt=prompt,
                tools=tools
            )

            results.append(result)

        return results