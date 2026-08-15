import os
import sys

# src 폴더를 Python이 찾을 수 있게 먼저 등록
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

# 그 다음 import
from toolcontract.loader import load_tools
from toolcontract.checks.description import check_description_quality
from toolcontract.checks.parameters import check_parameters
from toolcontract.checks.similarity import check_similarity
from toolcontract.checks.schema import check_schema

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


# ★ 새로 추가하는 부분
def analyze_tools(tools):
    """
    이미 불러온 Tool 목록을 검사하고
    발견된 문제들을 리스트로 반환합니다.
    CLI에서 사용합니다.
    """
    problems = []

    # 각 Tool 개별 검사
    for tool in tools:
        problems.extend(check_description_quality(tool))
        problems.extend(check_parameters(tool))
        problems.extend(check_schema(tool))

    # Tool 간 description 유사도 검사
    problems.extend(check_similarity(tools))

    return problems


# 기존 analyze 함수는 그대로 유지
def analyze(file_path):
    print(" AI 도구 명세서 품질 검사를 시작합니다...\n")
    print("-" * 50)

    # 1. JSON 파일에서 데이터 불러오기
    tools = load_tools(file_path)
    total_issues = 0

    # 2. 각 도구마다 순회하며 검사 실행
    for tool in tools:
        errors = []

        errors.extend(check_description_quality(tool))
        errors.extend(check_parameters(tool))
        errors.extend(check_schema(tool))

        if errors:
            for error in errors:
                print(error)
                total_issues += 1
        else:
            print(
                f"✅ [{tool.get('name')}] 통과: "
                f"설명이 충분히 명확합니다."
            )

    # 3. Tool 간 description 유사도 검사
    similarity_errors = check_similarity(tools)

    for error in similarity_errors:
        print(error)
        total_issues += 1

    print("-" * 50)
    print(
        f"🏁 검사 완료! "
        f"총 {total_issues}개의 개선점이 발견되었습니다."
    )


if __name__ == "__main__":
    # 프로젝트 폴더(ToolContract)를 기준으로 examples/tools.json의 경로를 찾습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    json_path = os.path.join(
        project_root,
        "examples",
        "tools.json"
    )

    # 분석기 실행
    analyze(json_path)