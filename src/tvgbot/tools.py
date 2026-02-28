import json

from .gmail import GmailClient
from .linkedin import LinkedinClient
from .twitter import TwitterClient
from .websearch import request_serper

twitter_client = TwitterClient()
linkedin_client = LinkedinClient()
gmail_client = GmailClient()

TOOL_REGISTRY = {}
WRITE_REQUIRES_APPROVAL = True
# TODO: we need to configure allowed_emails


def register_tool(schema, requires_approval=False):
    global TOOL_REGISTRY
    assert schema["name"] not in TOOL_REGISTRY

    def _register(fn):
        fn.schema = schema
        fn.requires_approval = requires_approval
        TOOL_REGISTRY[schema["name"]] = fn

    return _register


@register_tool(
    schema={
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
    },
    requires_approval=False,
)
def websearch(query):
    return request_serper(query)


@register_tool(
    schema={
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
    },
    requires_approval=False,
)
def get_tweet(tweet_id):
    return twitter_client.get_tweet(tweet_id)


@register_tool(
    schema={
        "name": "write_tweet",
        "description": "use this tool to write tweet on behalf of Vasudev Gupta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "text to tweet on twitter/X",
                },
            },
            "required": ["text"],
        },
    },
    requires_approval=WRITE_REQUIRES_APPROVAL,
)
def write_tweet(text):
    try:
        twitter_client.create_tweet(text)
        return json.dumps({"status": "SUCCESS"})
    except Exception as exception:
        return json.dumps({"status": "FAILED", "exception": exception})


@register_tool(
    schema={
        "name": "write_post_on_linkedin",
        "description": "use this tool to write post on linkedin behalf of Vasudev Gupta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "text to post on linkedin",
                }
            },
            "required": ["text"],
        },
    },
    requires_approval=WRITE_REQUIRES_APPROVAL,
)
def write_post_on_linkedin(text):
    try:
        linkedin_client.create_post(text)
        return json.dumps({"status": "SUCCESS"})
    except Exception as exception:
        return json.dumps({"status": "FAILED", "exception": exception})


@register_tool(
    schema={
        "name": "send_email",
        "description": "Use this tool to send email",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "One or more recipient email addresses. Use commas to separate multiple addresses.",
                },
                "subject": {
                    "type": "string",
                    "description": "subject of email.",
                },
                "body": {
                    "type": "string",
                    "description": "body of email.",
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
    requires_approval=WRITE_REQUIRES_APPROVAL,
)
def send_email(to, subject, body):
    try:
        gmail_client.send_email(to, subject, body)
        return json.dumps({"status": "SUCCESS"})
    except Exception as exception:
        return json.dumps({"status": "FAILED", "exception": exception})


@register_tool(
    schema={
        "name": "list_emails",
        "description": "Use this tool to list emails.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": ["string", "null"],
                    "description": (
                        "Optional Gmail search query string used to filter messages. "
                        "Must follow Gmail search syntax exactly as used in the Gmail web interface "
                        "(e.g., 'is:unread', 'from:example@gmail.com', "
                        "'newer_than:7d', 'after:2026/02/01 before:2026/02/28'). "
                        "Multiple filters can be combined using spaces."
                    ),
                    "default": None,
                },
                "max_results": {
                    "type": "integer",
                    "description": "max number of results to fetch.",
                    "default": 10,
                },
            },
        },
    },
    requires_approval=False,
)
def list_emails(query=None, max_results=10):
    emails = gmail_client.list_emails(query=query, max_results=max_results)
    return f"```json\n{json.dumps(emails, indent=2)}\n```"
