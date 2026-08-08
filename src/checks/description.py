def check_description_quality(tool: dict) -> list:
    """도구의 설명(description)이 명확하고 충분한지 검사합니다."""
    errors = []
    
    # 도구 이름과 설명 가져오기
    name = tool.get("name", "알 수 없는 도구")
    desc = tool.get("description", "")

    # 1. 설명이 아예 없는 경우 (치명적 오류)
    if not desc:
        errors.append(f"❌ [{name}] 오류: 도구 설명(description)이 누락되었습니다.")
        return errors

    # 2. 설명이 너무 짧고 모호한 경우 (경고)
    # 띄어쓰기 제외하고 길이가 짧으면 경고를 줍니다.
    if len(desc.replace(" ", "")) < 15:
        errors.append(f"⚠️ [{name}] 경고: 설명이 너무 짧습니다. ('{desc}') AI가 정확히 판단할 수 있게 더 구체적으로 적어주세요.")

    return errors