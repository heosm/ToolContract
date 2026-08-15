
def check_parameters(tool):
    errors = []

    tool_name = tool.get("name", "unknown")

    input_schema = tool.get("inputSchema", {})
    properties = input_schema.get("properties", {})

    for param_name, param_info in properties.items():
        description = param_info.get("description", "")

        if not description.strip():
            errors.append(
                f"⚠️ [TC101] [{tool_name}] "
                f"Parameter '{param_name}'에 description이 없습니다."
            )

    return errors