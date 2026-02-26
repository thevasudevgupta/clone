# python3 run.py

from dotenv import load_dotenv

load_dotenv()
import ipdb
from safeclaw.agent import Agent
from safeclaw.utils import convert_messages_to_string

agent = Agent(enable_thinking=True)
messages = agent.start()
ipdb.set_trace()
print(convert_messages_to_string(messages))
