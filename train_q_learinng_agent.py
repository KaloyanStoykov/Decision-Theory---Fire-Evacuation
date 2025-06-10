import gymnasium as gym
from utilities import create_env
from q_learning.agent import Agent


env = create_env(render=True)
agent = Agent(env=env)


def run():
    observation, _ = env.reset()

    for _ in range(10_000):
        action = agent.get_action(env.action_space)

        next_observation, reward, terminated, _, _ = env.step(action)

        agent.update(observation, action, reward, terminated, next_observation)
        observation = next_observation

        if terminated:
            observation, _ = env.reset()

    env.close()
    agent.save()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
