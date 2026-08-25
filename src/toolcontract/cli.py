import argparse
import json

from toolcontract.loader import load_tools
from toolcontract.analyzer import analyze_tools
from toolcontract.behavior.runner import BehaviorTestRunner
from toolcontract.behavior.evaluator import BehaviorEvaluator


def parse_expected_args(value):
    if not value:
        return {}

    # JSON 형식 지원
    try:
        parsed = json.loads(value)

        if isinstance(parsed, dict):
            return parsed

    except json.JSONDecodeError:
        pass

    # 간단한 key=value 형식 지원
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

            result[key] = raw_value

        return result

    except ValueError:
        raise argparse.ArgumentTypeError(
            "expected args 형식이 잘못되었습니다. "
            "예: order_id=123"
        )


def run_static(tools):
    problems = analyze_tools(tools)

    print()
    print("===== ToolContract Static Analysis =====")
    print(f"검사한 Tool 수: {len(tools)}")
    print(f"발견된 문제 수: {len(problems)}")
    print()

    if not problems:
        print("✅ Static Analysis PASS")
    else:
        for problem in problems:
            print(problem)

    return problems


def run_behavior(args, tools):
    print()
    print("===== ToolContract Behavior Test =====")
    print(f"Provider     : {args.provider}")
    print(f"Model        : {args.model}")
    print(f"Prompt       : {args.prompt}")
    print(f"Expected Tool: {args.expected_tool}")
    print()

    runner = BehaviorTestRunner(
        provider=args.provider,
        model=args.model,
    )

    evaluator = BehaviorEvaluator()

    results = runner.run_repeated_test(
        prompt=args.prompt,
        tools=tools,
        num_repeats=args.repeats,
    )

    for index, result in enumerate(results, start=1):
        print(
            f"[{index}회차] "
            f"Tool: {result.get('selected_tool')} / "
            f"Args: {result.get('arguments')}"
        )

    metrics = evaluator.calculate_metrics(
        results,
        args.expected_tool,
        args.expected_args,
    )

    print()
    print(f"Total Runs : {metrics['total_runs']}")
    print(f"Pass Count : {metrics['pass_count']}")
    print(f"Accuracy   : {metrics['accuracy']}%")
    print(f"Status     : {metrics['status']}")

    return metrics


def add_behavior_arguments(parser):
    parser.add_argument(
        "--provider",
        required=True,
        choices=["openai", "gemini", "groq"],
        help="Behavior Test에 사용할 LLM provider",
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Agent가 실제 사용하는 모델 ID",
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="LLM에 전달할 테스트 Prompt",
    )

    parser.add_argument(
        "--expected-tool",
        required=True,
        help="선택되어야 하는 Tool 이름",
    )

    parser.add_argument(
        "--expected-args",
        type=parse_expected_args,
        default={},
        help="예상 arguments. 예: order_id=123",
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="Behavior Test 반복 횟수",
    )


def main():
    parser = argparse.ArgumentParser(
        prog="toolcontract",
        description=(
            "Static analysis and behavior testing "
            "for AI Agent tool definitions."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ------------------------------
    # check
    # ------------------------------

    check_parser = subparsers.add_parser(
        "check",
        help="Tool definition을 정적 분석합니다.",
    )

    check_parser.add_argument(
        "file",
        help="Tool definition JSON 파일",
    )

    # ------------------------------
    # test
    # ------------------------------

    test_parser = subparsers.add_parser(
        "test",
        help="LLM Behavior Test를 실행합니다.",
    )

    test_parser.add_argument(
        "file",
        help="Tool definition JSON 파일",
    )

    add_behavior_arguments(test_parser)

    # ------------------------------
    # run
    # ------------------------------

    run_parser = subparsers.add_parser(
        "run",
        help="Static Analysis + Behavior Test를 실행합니다.",
    )

    run_parser.add_argument(
        "file",
        help="Tool definition JSON 파일",
    )

    add_behavior_arguments(run_parser)

    args = parser.parse_args()

    tools = load_tools(args.file)

    if args.command == "check":
        run_static(tools)

    elif args.command == "test":
        run_behavior(args, tools)

    elif args.command == "run":
        run_static(tools)
        run_behavior(args, tools)


if __name__ == "__main__":
    main()