# tests/test_behavior_run.py

import os

from dotenv import load_dotenv

from toolcontract.behavior.runner import BehaviorTestRunner
from toolcontract.behavior.evaluator import BehaviorEvaluator


# .env 로드
load_dotenv()


def test_behavior_run():
    # API 키 존재 확인
    assert os.getenv("GROQ_API_KEY"), "GROQ_API_KEY가 설정되지 않았습니다."

    # 테스트용 Tool
    tools = [
        {
            "name": "get_weather",
            "description": "특정 지역의 날씨를 가져옵니다.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "도시 이름, 예: Seoul"
                    }
                },
                "required": ["location"]
            }
        }
    ]

    prompt = "오늘 서울 날씨 어때?"

    expected_tool = "get_weather"
    expected_args = {
        "location": "Seoul"
    }

    print("\n===== Behavior Test 실행 =====")

    runner = BehaviorTestRunner()

    # 같은 프롬프트 3번 실행
    results = runner.run_repeated_test(
        prompt=prompt,
        tools=tools,
        num_repeats=3
    )

    evaluator = BehaviorEvaluator()

    metrics = evaluator.calculate_metrics(
        results,
        expected_tool,
        expected_args
    )

    print("\n--- 개별 실행 결과 ---")

    for i, result in enumerate(results, start=1):
        print(
            f"[{i}회차] "
            f"Tool: {result['selected_tool']} / "
            f"Args: {result['arguments']}"
        )

    print("\n--- 최종 Metrics ---")
    print(metrics)

    # 최소한 올바른 Tool을 선택했는지 검사
    for result in results:
        assert result["selected_tool"] == expected_tool