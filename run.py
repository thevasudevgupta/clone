# python3 run.py --server=discord

# ai should get its own credit card
# ai should be able to do any transaction
# need integration with twitter, linkedin, zepto, dominos, amazon, netflix, amazon prime, bookmyshow
# it should be controlled by simple discord channel

import fire

from dotenv import load_dotenv
assert load_dotenv()
from tvgbot.agent import Agent

def main(server: str = "local"):
    agent = Agent()
    agent.start(server=server)


if __name__ == "__main__":
    fire.Fire(main)
