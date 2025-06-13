from envs.ui.sprites import *
from envs.ui.sprites import load_srpite_map

load_srpite_map()

if __name__ == "__main__":
    # test_sprite(sprite_map["firefighter"]["shadow"], 32)
    display_sheet(env_sprites, ENV_SPRITE_ROWS, ENV_SPRITE_COLS)
    # display_sheet(fire_fighter_idle_sprites, 1, 6, 100)
    # test_sprite(sprite_map["cat"][0], 32)
#
