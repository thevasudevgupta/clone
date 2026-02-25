# python3 run.py

from dotenv import load_dotenv

load_dotenv()
from clone.agent import Agent
from clone.utils import convert_messages_to_string

# prompt = "Who is Vasudev Gupta?"
# messages = [{"role": "user", "content": prompt}]
agent = Agent(enable_thinking=False)
# messages = agent(messages, max_requests=4)
prompt = "how are you doing?"
messages = agent.start(prompt)

print(convert_messages_to_string(messages))
