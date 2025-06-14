import gymnasium as gym
from q_learning.agent import Agent
from q_learning.constants import N_EPISODES, RENDER, MAX_STEPS_PER_EPISODE
from q_learning.metrics import Metrics
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


config.static_fire_mode = True
# config.random_target_location = False
load_srpite_map()
agent = Agent()
metrics = Metrics()


def run():
    env = create_env()
    observation, _ = env.reset()

    for _ in range(N_EPISODES):
        for _ in range(MAX_STEPS_PER_EPISODE):
            action = agent.get_action(env.action_space, observation)

            next_observation, reward, terminated, _, info = env.step(action)
            metrics.log(reward, info["is_legal_move"], info["is_agent_dead"])
            agent.update(observation, action, reward, terminated, next_observation)
            observation = next_observation

            if terminated:
                break

        metrics.new_episode(agent.epsilon, info["distance"], agent.q_table, observation)
        agent.decay_epsilon()
        observation, _ = env.reset()

    env.close()
    metrics.save()
    agent.save()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Training interrupted")
        agent.save()
        metrics.save()
        pass
