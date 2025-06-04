import gymnasium as gym
import gymnasium.envs.registration

def create_env(render=True):
  gymnasium.envs.registration.register(
      id="FireFighterWorld",
      entry_point="envs:FireFighterWorld",
  )

  env = gym.make('FireFighterWorld', size=5, render_mode="human" if render else "rgb_array")
  env.reset(seed=42)
  
  return env
