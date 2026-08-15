# tests/test_behavior_run.py

import os
from dotenv import load_dotenv

# --- [1. 디버깅 및 환경 변수 로드] ---
print("--- 디버깅 시작 ---")
print(f"현재 실행 경로: {os.getcwd()}")
env_path = os.path.join(os.getcwd(), '.env')
print(f".env 파일 절대 경로: {env_path}")
print(f".env 파일 존재 여부: {os.path.exists(env_path)}")

# 명시적으로 해당 경로의 .env 파일을 로드합니다.
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    # 보안상 앞 5자리만 확인 (sk-pr...)
    print(f"API 키 로드 성공! (시작 부분: {api_key[:5]}...)")
else:
    print("[오류] API 키를 찾을 수 없습니다!")
print("--- 디버깅 끝 ---\n")

# --- [2. 모듈 Import] ---
from src.toolcontract.behavior.runner import BehaviorTestRunner
from src.toolcontract.behavior.evaluator import BehaviorEvaluator

# --- [3. 메인 실행부] ---
def main():
    tools = [{
        "name": "get_weather",
        "description": "특정 지역의 날씨를 가져옵니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "도시 이름, 예: Seoul"}
            },
            "required": ["location"]
        }
    }]

    prompt = "오늘 서울 날씨 어때?"
    expected_tool = "get_weather"
    expected_args = {"location": "Seoul"}

    print("🚀 GPT-4o Behavior Test 실행 중...")
    
    runner = BehaviorTestRunner()
    results = runner.run_repeated_test(prompt, tools, num_repeats=3)

    evaluator = BehaviorEvaluator()
    metrics = evaluator.calculate_metrics(results, expected_tool, expected_args)

    print("\n--- [개별 실행 결과] ---")
    for i, res in enumerate(results):
        print(f"[{i+1}회차] Tool: {res['selected_tool']} / Args: {res['arguments']}")

    print("\n--- [최종 Metrics] ---")
    print(metrics)

if __name__ == "__main__":
    main()