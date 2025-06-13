import gymnasium as gym
from q_learning.agent import Agent
from q_learning.constants import N_EPISODES, RENDER
from envs.constants import config
from envs.ui.sprites import load_srpite_map


def create_env():
    gym.envs.registration.register(
        id="FireFighterWorld",
        entry_point="envs:FireFighterWorld",
    )

    env = gym.make("FireFighterWorld", render_mode="human" if RENDER else "rgb_array")
    env.reset(seed=42)

    return env


config.chance_of_catching_fire = 0
config.random_target_location = False
load_srpite_map()
agent = Agent()


def run():
    env = create_env()
    observation, _ = env.reset()

    for _ in range(N_EPISODES):
        action = agent.get_action(env.action_space, observation)

        next_observation, reward, terminated, _, _ = env.step(action)

        agent.update(observation, action, reward, terminated, next_observation)
        observation = next_observation

        if terminated:
            agent.decay_epsilon()
            observation, _ = env.reset()

    env.close()
    agent.save()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Training interrupted")
        agent.save()
        pass
