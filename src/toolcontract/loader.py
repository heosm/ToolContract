
import json


def load_tools(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tools = json.load(file)

    return tools
