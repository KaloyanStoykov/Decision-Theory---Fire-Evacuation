import gymnasium as gym
from utilities import create_env
from q_learning.agent import Agent

n_episodes = 100_000
start_epsilon = 1.0

env = create_env(render=True)
agent = Agent(env=env)


def run():
    observation, _ = env.reset()

    for _ in range(1000):
        action = agent.get_action(env.action_space)

        next_observation, reward, terminated, _ = env.step(action)

        # agent.update(observation, action, reward, terminated, next_observation)
        observation = next_observation

        if terminated:
            observation, _ = env.reset()

    env.close()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
