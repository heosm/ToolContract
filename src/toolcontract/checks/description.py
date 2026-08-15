def check_description(tool):
    issues = []

    name = tool.get("name", "unknown")
    description = tool.get("description", "")

    # description이 아예 없는 경우
    if not description.strip():
        issues.append({
            "rule": "TC001",
            "level": "ERROR",
            "tool": name,
            "message": "Tool description이 없습니다."
        })
        return issues

    # description이 너무 짧은 경우
    if len(description.strip()) < 15:
        issues.append({
            "rule": "TC002",
            "level": "WARN",
            "tool": name,
            "message": "Tool description이 너무 짧습니다."
        })

    return issues
