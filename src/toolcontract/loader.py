import json


def load_tools(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tool = json.load(file)

    return tool


if __name__ == "__main__":
    tool = load_tools("examples/tool.json")
    print(tool)