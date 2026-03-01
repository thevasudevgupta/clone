import asyncio
import json
from copy import deepcopy

from anthropic import Anthropic

from .discord import DiscordClient
from .tools import TOOL_REGISTRY
from .utils import convert_messages_to_string, parse_assistant

SYSTEM_PROMPT = """
You are tvgbot, EA to Vasudev Gupta. Your job is to help Vasudev in day-to-day activities.
This includes:
* Manage his twitter and linkedin.
* Listen & reply to people over whatsapp and gmail.

With each message:
* learn about each person you interacted over whatsapp or gmail.
* Most importantly, document your learnings in your memory.

Memory
* TBD

Very Importantly
* Make sure to sound like Vasudev Gupta - so, no one can figure that its you and not Vasudev.

Extra Note:
If you get "tool execution was skipped as user didn't approve the tool" as tool_result,
this means that tool execution  was skipped for now and you need to save this tool in backlog for later execution whenever user asks again.
In this case, tell the user that tool execution was skipped for now as you requested and keeping this tool in backlog.
""".strip()


# TODO: add support for open-router as well - we want to understand how cogito model does here
# this way we will understand where our models stands compared to claude on real world tasks with our harness
class LocalAgent:
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

        self.tools = [tool.schema for tool in TOOL_REGISTRY.values()]
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

    def get_tool_calls(self, response):
        return [
            {
                "tool_call_id": part["id"],
                "name": part["name"],
                "arguments": part["input"],
            }
            for part in response["content"]
            if part["type"] == "tool_use"
        ]

    async def request_user_approval(self, prompt, **kwargs):
        return input(prompt)

    async def __call__(self, input_messages, max_requests=10, **kwargs):
        response = self.request_model(input_messages)
        output_messages = [response]

        tool_calls = self.get_tool_calls(response)
        num_requests = 1
        while len(tool_calls) > 0:
            if num_requests >= max_requests:
                break

            tool_results = []
            for tool_call in tool_calls:
                name, arguments = tool_call["name"], tool_call["arguments"]
                tool = TOOL_REGISTRY[name]
                if tool.requires_approval:
                    prompt = f'Please type "approve" to approve\n```\n{tool.__name__}(**{json.dumps(arguments, indent=2)})\n```'
                    user_response = await self.request_user_approval(prompt, **kwargs)
                    tool_result = (
                        tool(**arguments)
                        if user_response.lower() == "approve"
                        else "Skipped tool execution as user DID NOT approve."
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
            output_messages += [{"role": "user", "content": tool_results}]
            response = self.request_model(input_messages + output_messages)
            output_messages += [response]

            tool_calls = self.get_tool_calls(response)
            num_requests += 1

        return output_messages

    def start(self, max_requests_per_prompt=4):
        messages = []
        while True:
            prompt = input("--- User ---\n")
            messages += [{"role": "user", "content": prompt}]
            try:
                output_messages = asyncio.run(
                    self(messages, max_requests=max_requests_per_prompt)
                )
            except KeyboardInterrupt:
                break
            except Exception as exception:
                print(f"--- Failed with exception ---\n{exception}")
                messages.pop()
                continue
            messages += output_messages
            print("--- Assistant ---\n", parse_assistant(messages[-1]["content"]))
        return messages


# TODO: we should call anthropic api async
# TODO: we should do stream mode?
# TODO: discord thread can be supported nicely?
# TODO: maybe reasoning should be sent back within a file?
class DiscordAgent(LocalAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.discord_client = DiscordClient()

    async def request_user_approval(self, prompt, **kwargs):
        await self.discord_client.send_message(prompt, kwargs["channel_id"])
        response = await self.discord_client.receive_message()
        return response["content"]

    def start(self, max_requests_per_prompt=4):
        asyncio.run(self.start_discord(max_requests_per_prompt=max_requests_per_prompt))

    async def start_discord(self, max_requests_per_prompt=4):
        await self.discord_client.start()
        messages = []
        while True:
            message = await self.discord_client.receive_message()
            content, channel_id = message["content"], message["channel_id"]
            messages += [{"role": "user", "content": content}]

            try:
                output_messages = await self(
                    messages,
                    max_requests=max_requests_per_prompt,
                    channel_id=channel_id,
                )
            except KeyboardInterrupt:
                break
            except Exception as exception:
                await self.discord_client.send_message(
                    f"--- Failed with exception ---\n{exception}", channel_id
                )
                messages.pop()
                continue

            messages += output_messages
            content = parse_assistant(messages[-1]["content"])
            await self.discord_client.send_message(content, channel_id)

            internal_reasoning = self.get_internal_reasoning(output_messages)
            await self.discord_client.send_message(
                internal_reasoning,
                channel_id,
                self.discord_client.bot_last_message["message_id"],
            )

    # stream reasoning - message by message - ideally in thread
    def get_internal_reasoning(self, messages):
        reasoning = convert_messages_to_string(messages)
        if len(reasoning) > 1024:
            reasoning = "... " + reasoning[-1024:]
        return f"```\n{reasoning}\n```"
