def check_schema(tool):
    errors = []

    tool_name = tool.get("name", "unknown")
    input_schema = tool.get("inputSchema")

    # inputSchema가 없음
    if input_schema is None:
        errors.append(
            f"⚠️[TC201] [{tool_name}] inputSchema가 없습니다."
        )
        return errors

    # inputSchema type 검사
    if input_schema.get("type") != "object":
        errors.append(
            f"❌[TC202] [{tool_name}] inputSchema의 type은 object여야 합니다."
        )

    # properties 검사
    properties = input_schema.get("properties")

    if properties is None:
        errors.append(
            f"⚠️[TC203] [{tool_name}] inputSchema에 properties가 없습니다."
        )

    return errors