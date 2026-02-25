from copy import deepcopy

from anthropic import Anthropic

from .tools import TOOLS_REGISTRY


class Agent:
    def __init__(
        self,
        # model: str = "claude-opus-4-5-20251101",
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
        self.client = Anthropic()

    def request_model(self, messages):
        thinking = (
            {"type": "enabled", "budget_tokens": self.thinking_budget}
            if self.enable_thinking
            else {"type": "disabled"}
        )
        # https://platform.claude.com/docs/en/build-with-claude/extended-thinking#interleaved-thinking
        # above docs shows how to use beta headers for interleaved thinking
        # NOTE: we are using BETA API here because interleaved thinking is supported only for this one
        response = self.client.beta.messages.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            max_tokens=self.max_tokens,
            thinking=thinking,
            betas=["interleaved-thinking-2025-05-14"],
        )
        content = [part.model_dump() for part in response.content]
        return {"role": "assistant", "content": content}

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
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call["tool_call_id"],
                        "content": tool(**arguments),
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
