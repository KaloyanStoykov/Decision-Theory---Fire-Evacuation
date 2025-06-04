import gymnasium as gym
from utilities import create_env 
from q_learning.agent import Agent

n_episodes = 100_000
start_epsilon = 1.0

env = create_env(render=True)
agent = Agent(
    env=env,
    learning_rate=0.01,
    initial_epsilon=start_epsilon,
    epsilon_decay=start_epsilon / (n_episodes / 2), # reduce the exploration over time
    final_epsilon=0.1,
)

def run():
    for _ in range(1000):
        # this is where you would insert your policy
        action = env.action_space.sample()

        # step (transition) through the environment with the action
        # receiving the next observation, reward and if the episode has terminated or truncated
        observation, reward, terminated, truncated, info = env.step(action)

        # If the episode has ended then we can reset to start a new episode
        if terminated or truncated:
            observation, info = env.reset()

    env.close()


if __name__ == "__main__":
    try :
        run()
    except KeyboardInterrupt:
        pass