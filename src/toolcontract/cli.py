import sys

from loader import load_tools
from analyzer import analyze_tools


def main():
    print("ToolContract 실행됨")

    if len(sys.argv) < 2:
        print("사용법: python cli.py <tools.json>")
        return

    file_path = sys.argv[1]

    tools = load_tools(file_path)
    problems = analyze_tools(tools)

    print(f"{len(tools)}개의 Tool을 검사했습니다.")

    if not problems:
        print("문제가 없습니다.")
        return

    for problem in problems:
        print(f"[WARN] {problem['tool']}")
        print(f"       {problem['message']}")


if __name__ == "__main__":
    main()