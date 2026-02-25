# python3 run.py

from dotenv import load_dotenv

load_dotenv()
from clone.agent import Agent
from clone.utils import convert_messages_to_string

prompt = "Who is Vasudev Gupta?"
messages = [{"role": "user", "content": prompt}]

agent = Agent(enable_thinking=True)
messages = agent(messages, max_requests=4)

print(convert_messages_to_string(messages))
