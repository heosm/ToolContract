import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


PROVIDER_CONFIG = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
}


class BehaviorTestRunner:
    def __init__(self, provider: str, model: str):
        provider = provider.lower().strip()

        if provider not in PROVIDER_CONFIG:
            supported = ", ".join(PROVIDER_CONFIG.keys())
            raise ValueError(
                f"지원하지 않는 provider입니다: {provider}. "
                f"지원 목록: {supported}"
            )

        if not model or not model.strip():
            raise ValueError("model을 지정해야 합니다.")

        config = PROVIDER_CONFIG[provider]

        api_key = os.getenv(config["api_key_env"])

        if not api_key:
            raise ValueError(
                f"{config['api_key_env']}를 찾을 수 없습니다. "
                f".env 또는 환경 변수를 확인하세요."
            )

        client_args = {
            "api_key": api_key,
        }

        if config["base_url"]:
            client_args["base_url"] = config["base_url"]

        self.client = OpenAI(**client_args)
        self.provider = provider
        self.model = model

    def _convert_tools(self, tools):
        """
        ToolContract/MCP 형식을 OpenAI-compatible
        Function Calling 형식으로 변환합니다.
        """

        converted = []

        for tool in tools:
            # 이미 OpenAI Function Calling 형식인 경우
            if tool.get("type") == "function" and "function" in tool:
                converted.append(tool)
                continue

            input_schema = tool.get(
                "inputSchema",
                {
                    "type": "object",
                    "properties": {},
                },
            )

            converted.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": input_schema,
                    },
                }
            )

        return converted

    def run_single_test(self, prompt, tools):
        openai_tools = self._convert_tools(tools)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            tools=openai_tools,
            tool_choice="auto",
        )

        message = response.choices[0].message

        result = {
            "selected_tool": None,
            "arguments": None,
            "raw_response": message.content,
            "raw_tool_calls": None,
        }

        if message.tool_calls:
            tool_call = message.tool_calls[0]

            result["selected_tool"] = tool_call.function.name
            result["raw_tool_calls"] = message.tool_calls

            try:
                result["arguments"] = json.loads(
                    tool_call.function.arguments
                )
            except (json.JSONDecodeError, TypeError):
                result["arguments"] = tool_call.function.arguments

        return result

    def run_repeated_test(
        self,
        prompt,
        tools,
        num_repeats=5,
    ):
        results = []

        for _ in range(num_repeats):
            results.append(
                self.run_single_test(
                    prompt=prompt,
                    tools=tools,
                )
            )

        return results