def check_description_quality(tool):
    errors = []

    name = tool.get("name", "unknown")
    description = tool.get("description", "")

    # TC001: 설명 없음
    if not isinstance(description, str) or not description.strip():
        errors.append(
            f"❌ [TC001] [{name}] Tool description이 없습니다."
        )
        return errors

    description = description.strip()

    # TC002: 지나치게 짧은 설명
    if len(description) < 8:
        errors.append(
            f"⚠️ [TC002] [{name}] Tool description이 지나치게 짧습니다."
        )

    # TC003: 모호한 표현
    vague_words = [
        "처리합니다",
        "관련",
        "작업합니다",
        "요청을 처리",
        "정보를 처리"
    ]

    found_words = [
        word for word in vague_words
        if word in description
    ]

    if found_words:
        errors.append(
            f"⚠️ [TC003] [{name}] 모호한 표현이 포함되어 있습니다: "
            + ", ".join(found_words)
        )

    return errors