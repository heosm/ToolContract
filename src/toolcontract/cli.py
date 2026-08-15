# src/toolcontract/cli.py

import argparse
import json

from toolcontract.loader import load_tools
from toolcontract.analyzer import analyze_tools

from toolcontract.behavior.runner import BehaviorTestRunner
from toolcontract.behavior.evaluator import BehaviorEvaluator


def run_static_analysis(file_path):
    """
    Tool 명세 정적 분석
    """
    print("\n===== ToolContract Static Analysis =====")

    tools = load_tools(file_path)
    problems = analyze_tools(tools)

    print(f"\n검사한 Tool 수: {len(tools)}")

    if not problems:
        print("문제가 없습니다.")
        return

    print(f"발견된 문제 수: {len(problems)}\n")

    for problem in problems:
        # analyzer 결과가 dict인 경우
        if isinstance(problem, dict):
            rule = problem.get("rule", "UNKNOWN")
            level = problem.get("level", "WARN")
            tool = problem.get("tool", "unknown")
            message = problem.get("message", "")

            print(
                f"[{level}] [{rule}] "
                f"{tool}: {message}"
            )

        # 문자열 형태로 반환하는 경우
        else:
            print(problem)


def run_behavior_test(
    file_path,
    prompt,
    expected_tool,
    expected_args,
    repeats
):
    """
    실제 LLM을 이용한 Tool 선택 Behavior Test
    """
    print("\n===== ToolContract Behavior Test =====")

    tools = load_tools(file_path)

    runner = BehaviorTestRunner()

    results = runner.run_repeated_test(
        prompt=prompt,
        tools=tools,
        num_repeats=repeats
    )

    evaluator = BehaviorEvaluator()

    metrics = evaluator.calculate_metrics(
        results,
        expected_tool,
        expected_args
    )

    print(f"\nPrompt: {prompt}")
    print(f"Expected Tool: {expected_tool}")

    print("\n--- 개별 실행 결과 ---")

    for i, result in enumerate(results, start=1):
        print(
            f"[{i}회차] "
            f"Tool: {result['selected_tool']} / "
            f"Args: {result['arguments']}"
        )

    print("\n--- 최종 Metrics ---")
    print(f"Total Runs : {metrics.get('total_runs')}")
    print(f"Pass Count : {metrics.get('pass_count')}")
    print(f"Accuracy   : {metrics.get('accuracy')}%")
    print(f"Status     : {metrics.get('status')}")


def parse_expected_args(value):
    """
    expected arguments를 파싱합니다.

    지원 형식:
    user_id=12345

    여러 개일 경우:
    user_id=12345,name=kim

    기존 JSON 형식도 지원:
    {"user_id": "12345"}
    """

    value = value.strip()

    # 기존 JSON 방식도 계속 지원
    try:
        parsed = json.loads(value)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # key=value 방식
    result = {}

    try:
        pairs = value.split(",")

        for pair in pairs:
            if "=" not in pair:
                raise ValueError

            key, raw_value = pair.split("=", 1)

            key = key.strip()
            raw_value = raw_value.strip()

            if not key:
                raise ValueError

            # 숫자 / bool / null 등은 가능하면
            # 자동으로 Python 타입으로 변환
            try:
                parsed_value = json.loads(raw_value)
            except json.JSONDecodeError:
                # 일반 문자열이면 그대로 사용
                parsed_value = raw_value

            result[key] = parsed_value

        return result

    except ValueError:
        raise argparse.ArgumentTypeError(
            "expected args 형식이 잘못되었습니다. "
            "예: user_id=12345"
        )

def main():
    parser = argparse.ArgumentParser(
        prog="toolcontract",
        description="AI Agent Tool 명세를 검사하고 LLM Behavior Test를 실행합니다."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # -------------------------------------------------
    # check
    # -------------------------------------------------

    check_parser = subparsers.add_parser(
        "check",
        help="Tool 명세를 정적 분석합니다."
    )

    check_parser.add_argument(
        "file",
        help="Tool JSON 파일 경로"
    )

    # -------------------------------------------------
    # test
    # -------------------------------------------------

    test_parser = subparsers.add_parser(
        "test",
        help="LLM Behavior Test를 실행합니다."
    )

    test_parser.add_argument(
        "file",
        help="Tool JSON 파일 경로"
    )

    test_parser.add_argument(
        "--prompt",
        required=True,
        help="LLM에 전달할 테스트 Prompt"
    )

    test_parser.add_argument(
        "--expected-tool",
        required=True,
        help="선택되어야 하는 Tool 이름"
    )

    test_parser.add_argument(
        "--expected-args",
        required=True,
        type=parse_expected_args,
        help="기대하는 arguments(JSON)"
    )

    test_parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="반복 테스트 횟수 (기본값: 3)"
    )

    # -------------------------------------------------
    # run
    # -------------------------------------------------

    run_parser = subparsers.add_parser(
        "run",
        help="정적 분석과 Behavior Test를 모두 실행합니다."
    )

    run_parser.add_argument(
        "file",
        help="Tool JSON 파일 경로"
    )

    run_parser.add_argument(
        "--prompt",
        required=True,
        help="LLM에 전달할 테스트 Prompt"
    )

    run_parser.add_argument(
        "--expected-tool",
        required=True,
        help="선택되어야 하는 Tool 이름"
    )

    run_parser.add_argument(
        "--expected-args",
        required=True,
        type=parse_expected_args,
        help="기대하는 arguments(JSON)"
    )

    run_parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="반복 테스트 횟수 (기본값: 3)"
    )

    args = parser.parse_args()

    # -------------------------------------------------
    # 명령 실행
    # -------------------------------------------------

    if args.command == "check":

        run_static_analysis(
            args.file
        )

    elif args.command == "test":

        run_behavior_test(
            file_path=args.file,
            prompt=args.prompt,
            expected_tool=args.expected_tool,
            expected_args=args.expected_args,
            repeats=args.repeats
        )

    elif args.command == "run":

        run_static_analysis(
            args.file
        )

        run_behavior_test(
            file_path=args.file,
            prompt=args.prompt,
            expected_tool=args.expected_tool,
            expected_args=args.expected_args,
            repeats=args.repeats
        )


if __name__ == "__main__":
    main()