import json
from copy import deepcopy

from anthropic import Anthropic

from .tools import TOOLS_REGISTRY

SYSTEM_PROMPT = """
You are EA to Vasudev Gupta and manages his personal social handles such as twitter, linkedin, whatsapp. 

Make sure to sound like Vasudev - so, no one can figure out whether you are posting or Vasudev is.

If you get "tool execution was skipped as user didn't approve the tool" as tool_result,
this means that tool execution  was skipped for now and you need to save this tool in backlog for later execution whenever user asks again.
In this case, tell the user that tool execution was skipped for now as you requested and keeping this tool in backlog.
""".strip()


class Agent:
    def __init__(
        self,
        model: str = "claude-sonnet-4-5",
        max_tokens: int = 16_384,
        enable_thinking: bool = False,
        thinking_budget: int = 14_336,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.thinking_budget = thinking_budget

        self.tools = [tool.schema for tool in TOOLS_REGISTRY.values()]
        self.system_prompt = SYSTEM_PROMPT

        self.client = Anthropic()

    def request_model(self, messages):
        thinking = (
            {"type": "enabled", "budget_tokens": self.thinking_budget}
            if self.enable_thinking
            else {"type": "disabled"}
        )
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            system=self.system_prompt,
            max_tokens=self.max_tokens,
            thinking=thinking,
        )
        content = [part.model_dump() for part in response.content]
        return {"role": "assistant", "content": content}

    # TODO: are you sure that we want to modify messages in-place?
    def __call__(self, messages, max_requests=10):
        messages = deepcopy(messages)

        response = self.request_model(messages)
        messages.append(response)

        tool_calls = [
            {
                "tool_call_id": part["id"],
                "name": part["name"],
                "arguments": part["input"],
            }
            for part in response["content"]
            if part["type"] == "tool_use"
        ]
        num_requests = 1
        while len(tool_calls) > 0:
            if num_requests >= max_requests:
                break

            tool_results = []
            for tool_call in tool_calls:
                name, arguments = tool_call["name"], tool_call["arguments"]
                tool = TOOLS_REGISTRY[name]()
                if tool.requires_approval:
                    user_approval = input(
                        f'Please type "y" to approve tool_call={json.dumps(tool_call, indent=2)}'
                    )
                    if user_approval == "y":
                        tool_result = tool(**arguments)
                    else:
                        tool_result = (
                            "tool execution was skipped as user didn't approve the tool"
                        )
                else:
                    tool_result = tool(**arguments)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call["tool_call_id"],
                        "content": tool_result,
                    }
                )
            messages.append({"role": "user", "content": tool_results})
            response = self.request_model(messages)
            messages.append(response)

            tool_calls = [
                {
                    "tool_call_id": part["id"],
                    "name": part["name"],
                    "arguments": part["input"],
                }
                for part in response["content"]
                if part["type"] == "tool_use"
            ]
            num_requests += 1

        return messages

    def start(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        print("User:", prompt)
        for _ in range(5):
            messages = self(messages, max_requests=4)
            print("Assistant:", messages[-1]["content"])
            prompt = input("User: ")
            messages += [{"role": "user", "content": prompt}]
        return messages
