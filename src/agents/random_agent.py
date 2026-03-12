import random
from marioai.agent import Agent

__all__ = ['RandomAgent']

class RandomAgent(Agent):
    def act(self):
        return [0, 1, 0, random.randint(0, 0), random.randint(0, 0)]
        return [0, 1, 0, random.randint(0, 1), random.randint(0, 1)]
    