import json


def convert_messages_to_string(messages):
    string = []
    for x in messages:
        role = x["role"]

        if role == "user":
            if isinstance(x["content"], list):
                content = []
                for part in x["content"]:
                    if part["type"] == "tool_result":
                        tool_result = part["content"]
                        content.append(
                            f"<tool_result>\nID: {part['tool_use_id']}\n{tool_result}\n</tool_result>"
                        )
                    else:
                        raise f"Invalid type={part['type']}"
                content = "\n".join(content)
            else:
                content = x["content"]
            res = f"<user>\n{content}\n</user>"

        elif role == "assistant":
            content = []
            for part in x["content"]:
                if part["type"] == "thinking":
                    content.append(f"<think>\n{part['thinking']}\n</think>")
                elif part["type"] == "text":
                    content.append(f"<answer>\n{part['text']}\n</answer>")
                elif part["type"] == "tool_use":
                    tool_call = {
                        "id": part["id"],
                        "name": part["name"],
                        "arguments": part["input"],
                    }
                    tool_call = json.dumps(tool_call, indent=2)
                    content.append(f"<tool_call>\n{tool_call}\n</tool_call>")
                else:
                    raise f"Invalid type={part['type']}"

            content = "\n".join(content)
            res = f"<assistant>\n{content}\n</assistant>"
        else:
            raise ValueError(f"Invalid role={role}")

        string.append(res)
    return "\n".join(string)
