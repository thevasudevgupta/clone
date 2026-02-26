import json
import os

import requests

from .utils import get_tweepy

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
    requires_approval = False

    schema = {
        "name": "web_search",
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


# TODO: implement webfetch tool asap!
# TODO: model should summarise its history somewhere
# basically manage its own memory - so, we can drop super long conversations
# shall we do in aws s3? we should store versions?
# TODO: implement whatsapp tomorrow; and lets chat with some friends over there using safeclaw
# and see if they feel natural
# we also need to let safeclaw know how we talk
# probably need some kinda memory about me - lets use YAML for that?
# TODO: agent should get triggered only once every 10 seconds?


@register_tool
class GetTweetTool:
    requires_approval = False
    schema = {
        "name": "get_tweet",
        "description": "use this tool to fetch & read tweets",
        "input_schema": {
            "type": "object",
            "properties": {
                "tweet_id": {
                    "type": "string",
                    "description": "tweet ID which you want to read",
                },
            },
            "required": ["tweet_id"],
        },
    }

    def __init__(self):
        self.client = get_tweepy()
        self._kwargs = {
            "user_auth": True,
            "tweet_fields": ["conversation_id", "author_id", "note_tweet"],
        }

    def _get_text(self, tweet):
        return tweet.note_tweet["text"] if hasattr(tweet, "note_tweet") else tweet.text

    def __call__(self, tweet_id: str):
        tweet = self.client.get_tweet(tweet_id, **self._kwargs).data
        # TODO: why do we need to handle 1st tweet separately?
        res = [self._get_text(tweet)]
        query = f"conversation_id:{tweet.conversation_id} from:{tweet.author_id}"
        thread = self.client.search_recent_tweets(query=query, **self._kwargs)
        if thread.data is not None:
            for tweet in sorted(thread.data, key=lambda x: x.id):
                res += [self._get_text(tweet)]
        return "\n".join(res)


# TODO: add support of quote tweet, reply tweet?
@register_tool
class WriteTweetTool:
    requires_approval = True
    schema = {
        "name": "write_tweet",
        "description": "use this tool to write tweet on behalf of @thevasudevgupta",
        "input_schema": {
            "type": "object",
            "properties": {
                "tweet": {
                    "type": "string",
                    "description": "text of tweet; Note: tweet will be actually be published on twitter/X.",
                },
            },
            "required": ["tweet"],
        },
    }

    def __init__(self):
        self.client = get_tweepy()

    def __call__(self, tweet):
        try:
            self.client.create_tweet(text=tweet)
            return "Tweet succesfully published on @thevasudevgupta account."
        except Exception as e:
            return f"write_tweet failed with exception: {e}"
