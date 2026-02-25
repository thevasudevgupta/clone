import json
import os

import requests

TOOLS_REGISTRY = {}
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def register_tool(cls):
    global TOOLS_REGISTRY
    TOOLS_REGISTRY[cls.schema["name"]] = cls
    return cls


def request_serper(query: str):
    assert SERPER_API_KEY is not None
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    response = json.loads(response.text)["organic"]
    result = []
    for i, doc in enumerate(response, 1):
        title, snippet = doc["title"], doc.get("snippet")
        result.append(f'[{i}]"{title}\n{snippet}"')
    result = "\n\n".join(result)
    return f"```\n{result}\n```"


@register_tool
class WebSearchTool:
    schema = {
        "name": "websearch",
        "description": "web search tool which has acess to Google.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "query which you want to search over Google.",
                }
            },
            "required": ["query"],
        },
    }

    def __call__(self, query: str):
        return request_serper(query)
