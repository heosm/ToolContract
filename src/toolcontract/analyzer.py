import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
# 다른 폴더(checks, loader)의 파이썬 파일을 잘 불러오도록 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from toolcontract.loader import load_tools
from checks.description import check_description_quality

def analyze(file_path):
    print(f" AI 도구 명세서 품질 검사를 시작합니다...\n")
    print("-" * 50)
    
    # 1. JSON 파일에서 데이터 불러오기
    tools = load_tools(file_path)
    total_issues = 0
    
    # 2. 각 도구마다 순회하며 검사 실행
    for tool in tools:
        # description.py에서 만든 검사 함수 실행
        errors = check_description_quality(tool)
        
        if errors:
            for error in errors:
                print(error)
                total_issues += 1
        else:
            print(f"✅ [{tool.get('name')}] 통과: 설명이 충분히 명확합니다.")
            
    print("-" * 50)
    print(f"🏁 검사 완료! 총 {total_issues}개의 개선점이 발견되었습니다.")

if __name__ == "__main__":
    # 프로젝트 폴더(ToolContract)를 기준으로 examples/tools.json의 경로를 찾습니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    json_path = os.path.join(project_root, "examples", "tools.json")
    
    # 분석기 실행
    analyze(json_path)