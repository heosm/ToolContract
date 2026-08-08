def analyze_tools(tools):
    problems = []

    for tool in tools:
        if not tool.get("description"):
            problems.append({
                "tool": tool.get("name", "unknown"),
                "message": "description이 없습니다."
            })

    return problems
