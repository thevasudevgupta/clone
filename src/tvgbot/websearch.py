import json
import os

import requests


def request_serper(query: str):
    api_key = os.getenv("SERPER_API_KEY")
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": api_key,
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
