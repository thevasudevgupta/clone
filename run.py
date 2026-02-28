# python3 run.py --server=discord --max_requests_per_prompt=20

# PLAN
# ai should get its own credit card
# ai should be able to do any transaction
# need integration with twitter, linkedin, zepto, dominos, amazon, netflix, amazon prime, bookmyshow
# can we use browserbase for integeration of these?
# implement memory: each important detail, which could be needed in future, should be stored in memory

# DONE
# it should be controlled by simple discord channel

import fire

from dotenv import load_dotenv
assert load_dotenv()
from tvgbot.agent import Agent

def main(server: str = "local", max_requests_per_prompt: int = 4):
    agent = Agent()
    agent.start(server=server, max_requests_per_prompt=max_requests_per_prompt)


if __name__ == "__main__":
    fire.Fire(main)
