import hashlib
import json

import requests


def make_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response


def hash_sha256(string):
    return hashlib.sha256(string.encode()).hexdigest()


def get_answer(assistant_content):
    return "\n".join(
        [part["text"] for part in assistant_content if part["type"] == "text"]
    )


def get_truncated(text, max_chars=64):
    if len(text) <= max_chars:
        return text
    return text[: max_chars // 2].strip() + " ... " + text[-max_chars // 2 :].strip()


def parse_user(user_content):
    if isinstance(user_content, str):
        return user_content
    res = []
    for part in user_content:
        if part["type"] == "tool_result":
            tool_result = f"<tool_result>\nID: {part['tool_use_id']}\n{get_truncated(part['content'])}\n</tool_result>"
            res.append(tool_result)
        else:
            raise f"Invalid type={part['type']}"
    return "\n".join(res)


def parse_assistant(assistant_content):
    res = []
    for part in assistant_content:
        if part["type"] == "thinking":
            res.append(f"<think>\n{part['thinking']}\n</think>")
        elif part["type"] == "text":
            res.append(f"<answer>\n{part['text']}\n</answer>")
        elif part["type"] == "tool_use":
            tool_call = {
                "id": part["id"],
                "name": part["name"],
                "arguments": part["input"],
            }
            tool_call = json.dumps(tool_call, indent=2)
            res.append(f"<tool_call>\n{tool_call}\n</tool_call>")
        else:
            raise f"Invalid type={part['type']}"
    return "\n".join(res)


def convert_messages_to_string(messages):
    string = []
    for x in messages:
        role = x["role"]
        if role == "user":
            content = parse_user(x["content"])
            res = f"<user>\n{content}\n</user>"
        elif role == "assistant":
            content = parse_assistant(x["content"])
            res = f"<assistant>\n{content}\n</assistant>"
        else:
            raise ValueError(f"Invalid role={role}")
        string.append(res)
    return "\n".join(string)
