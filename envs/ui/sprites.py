import pygame
from envs.constants import config
import os # Import os for path manipulation

# 8x28 is likely the dimension of the entire sprite sheet in terms of individual 16x16 sprites
# 128x432 is the pixel dimension of the sheet
ENV_SPRITE_ROWS = 27 # This seems correct for the "4 BigSet.png" if it's 16px sprites
ENV_SPRITE_COLS = 8
PADDING = 0 # Padding between sprites when creating a sheet

# --- Helper functions ---

# Function to scale a single sprite to the config.square_size
def scale(sprite, size=config.square_size):
    return pygame.transform.scale(sprite, (size, size))

# Function to load a sprite sheet and chop it into individual sprites
def load_sprite_sheet(filename, rows, cols, size):
    # Temporarily initialize pygame if it's not already
    is_pygame_initialized_here = False
    if not pygame.get_init():
        pygame.init()
        # No need for display.set_mode here as it's not rendering, just loading
        is_pygame_initialized_here = True

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_rect = sheet.get_rect()

        sprites = []
        # Iterate through the sheet to extract subsurfaces
        for y_offset in range(rows): # Use row index for cleaner loop
            if y_offset * size > sheet_rect.height: # Check if we're trying to go beyond sheet height
                break # Avoid IndexError if sheet is smaller than expected rows
            row_sprites = []
            for x_offset in range(cols): # Use col index
                if x_offset * size > sheet_rect.width: # Check if we're trying to go beyond sheet width
                    break # Avoid IndexError if sheet is smaller than expected cols

                # Ensure the subsurface doesn't go out of bounds of the actual image
                sub_rect_x = x_offset * size
                sub_rect_y = y_offset * size
                sub_rect_width = min(size, sheet_rect.width - sub_rect_x)
                sub_rect_height = min(size, sheet_rect.height - sub_rect_y)

                if sub_rect_width > 0 and sub_rect_height > 0:
                    row_sprites.append(sheet.subsurface(pygame.Rect(sub_rect_x, sub_rect_y, sub_rect_width, sub_rect_height)).copy())
            if row_sprites: # Only add if row has sprites
                sprites.append(row_sprites)
    except pygame.error as e:
        print(f"Error loading sprite sheet {filename}: {e}")
        sprites = [] # Return empty if error
    finally:
        if is_pygame_initialized_here:
            pygame.quit() # Quit pygame if we initialized it

    return sprites


# Function to load fire sprites specifically
def load_fire_sprites():
    fires = []
    is_pygame_initialized_here = False
    if not pygame.get_init():
        pygame.init()
        # No need for display.set_mode, just loading
        is_pygame_initialized_here = True

    try:
        for i in range(1, 5): # Assumes Fogo_1.png to Fogo_4.png
            filepath = os.path.join("assets", "Fogo_" + str(i) + ".png")
            sheet = pygame.image.load(filepath).convert_alpha()
            # These values (1024/28, 16, piece*4) suggest a specific internal layout of your fire images
            # If Fogo_*.png are individual frames of fire animation, they should be loaded differently.
            # Assuming these are sheets that contain a specific fire sprite
            piece = 1024 / 28
            offset = piece * 16 # This offset picks a specific part of the image
            frame = scale(
                sheet.subsurface(pygame.Rect(offset, offset, piece * 4, piece * 4)).copy()
            )
            fires.append(frame)
    except pygame.error as e:
        print(f"Error loading fire sprite Fogo_{i}.png: {e}")
        fires = [] # Return empty if error
    finally:
        if is_pygame_initialized_here:
            pygame.quit()
    return fires

# --- Core sprite loading ---

# Load the main environment sprite sheet
# Pygame should only be initialized once for the main display loop.
# Initializing and quitting pygame multiple times in load_sprite_sheet/load_fire_sprites
# is generally bad practice and can lead to issues.
# Let's ensure Pygame is initialized only once for the entire script.

# Pygame initialization for the whole sprites.py file
pygame.init()
# A temporary display surface is still needed for image loading
_temp_screen = pygame.display.set_mode((1, 1), pygame.HIDDEN) # Create a hidden display to avoid flicker


env_sprites = [
    [scale(sprite) for sprite in sprite_list]
    for sprite_list in load_sprite_sheet(
        "assets/4 BigSet.png", ENV_SPRITE_ROWS, ENV_SPRITE_COLS, 16 # Corrected order: rows, cols
    )
]

# --- Character and item specific sprite processing functions ---

def fix_firefighter(sprite_100x100_sheet, with_shadow=True):
    # This function expects a 100x100 sprite from the sheet and extracts a 24x24 sub-sprite
    # and recolors it.
    size = 24 # The actual size of the firefighter sprite within the 100x100 block
    x_offset_in_100 = (100 - size) // 2 # = 38 (instead of 42 based on (100-24)/2)
    y_offset_in_100 = (100 - size) // 2 # = 38

    # Use the actual size to ensure the rect is correct
    firefighter_sprite_cut = sprite_100x100_sheet.subsurface(pygame.Rect(x_offset_in_100, y_offset_in_100, size, size)).copy()
    firefighter_sprite_scaled = scale(firefighter_sprite_cut) # Scale to config.square_size

    def hex_to_rgba(hex_color):
        hex_color = hex_color.lstrip("#").lstrip("0x")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    colors_to_replace = [
        (hex_to_rgba(old), hex_to_rgba(new))
        for old, new in [
            ("#607581", "#672020"), # Example color changes
            ("#C2CDD2", "#8F3838"),
            ("#9BADB7", "#672020"),
            ("#C5D0D5", "#8F3838"),
            ("#425C6B", "#561D1D"),
            ("#5D6C75", "#561D1D"),
            ("#6F828D", "#511D1D"),
            ("#7F909A", "#511D1D"),
            ("#7B4E16", "#B19E9A"),
            ("#8D6534", "#B19E9A"), # Typo fixed: "#8D6534"
        ]
    ]

    # Apply color replacements
    width, height = firefighter_sprite_scaled.get_size()
    for x in range(width):
        for y in range(height):
            current_color = firefighter_sprite_scaled.get_at((x, y))
            for old_color, new_color in colors_to_replace:
                # Compare RGBA values, not just RGB, as alpha can be part of it
                if current_color == old_color:
                    firefighter_sprite_scaled.set_at((x, y), new_color)
                    break # Move to next pixel after replacement

    if with_shadow:
        # Load and process shadow
        # Ensure Soldier-Shadow.png is a 100x100 sprite as well if it's from a sheet
        shadow_sheet = load_sprite_sheet("assets/Soldier-Shadow.png", 1, 1, 100)
        if shadow_sheet and shadow_sheet[0]:
            raw_shadow = shadow_sheet[0][0]
            # Extract the same 24x24 sub-sprite and scale it
            shadow_cut = raw_shadow.subsurface(pygame.Rect(x_offset_in_100, y_offset_in_100, size, size)).copy()
            shadow_scaled = scale(shadow_cut)
            shadow_scaled.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            shadow_scaled.blit(firefighter_sprite_scaled, (0, 0)) # Blit the colored sprite onto the shadow
            return shadow_scaled
        else:
            print("Warning: Soldier-Shadow.png not loaded correctly. Returning firefighter without shadow.")
            return firefighter_sprite_scaled
    else:
        return firefighter_sprite_scaled


def fix_cat(sprite_raw):
    # This expects an already loaded sprite (likely a 32x32 from the cat.png sheet)
    # and will scale it, potentially applying padding.
    PADDING_CAT = 34 # This padding likely means it will make the cat smaller than config.square_size
    return scale(sprite_raw, config.square_size - PADDING_CAT)


# --- Define the main sprite_map dictionary ---
sprite_map = {
    "fires": load_fire_sprites(),
    "firefighter": {
        "idle": [
            fix_firefighter(s) for s in load_sprite_sheet("assets/Soldier-Idle.png", 1, 6, 100)[0]
        ],
        # Renamed "dying" to "death" to match `FireFighter.kill()` logic
        "death": [
            fix_firefighter(s) for s in (
                load_sprite_sheet("assets/Soldier-Hurt.png", 1, 3, 100)[0] +
                load_sprite_sheet("assets/Soldier-Death.png", 1, 4, 100)[0]
            )
        ],
        "walk": [ # Added explicit walk animation if you have Soldier-Walk.png
            fix_firefighter(s) for s in load_sprite_sheet("assets/Soldier-Walk.png", 1, 6, 100)[0]
        ],
        "put_out_fire": [
            fix_firefighter(s, False) for s in load_sprite_sheet(
                "assets/Soldier-Attack01_Effect.png", 1, 6, 100
            )[0][3:5] # Taking specific frames from the attack sheet
        ],
        # Add a "death_final" if your FireFighter class uses it as a distinct state
        "death_final": [fix_firefighter(load_sprite_sheet("assets/Soldier-Death.png", 1, 4, 100)[0][-1])]
    },
    "cat": { # <--- FIX: Made 'cat' a dictionary for animation states
        "idle": [ # <--- 'idle' key with a list of sprites
            fix_cat(s) for s in load_sprite_sheet("assets/cat.png", 1, 4, 32)[0]
        ],
        # Add other cat animations here if you have them, e.g., "scared", "running"
    },
    # Ensure correct indices for env_sprites, as load_sprite_sheet order changed.
    # If ENV_SPRITE_ROWS was 27 and ENV_SPRITE_COLS was 8 for 16px sprites:
    "wall": {
        "front": env_sprites[20][3] if len(env_sprites) > 20 and len(env_sprites[20]) > 3 else None,
        "top": env_sprites[19][3] if len(env_sprites) > 19 and len(env_sprites[19]) > 3 else None,
        "half": env_sprites[21][3] if len(env_sprites) > 21 and len(env_sprites[21]) > 3 else None,
    },
    "floor_tile": env_sprites[19][1] if len(env_sprites) > 19 and len(env_sprites[19]) > 1 else None,
    "window": env_sprites[21][6] if len(env_sprites) > 21 and len(env_sprites[21]) > 6 else None,
    "picture": env_sprites[21][7] if len(env_sprites) > 21 and len(env_sprites[21]) > 7 else None,
    "bed": {
        "red": env_sprites[23][0] if len(env_sprites) > 23 and len(env_sprites[23]) > 0 else None,
        "blue": env_sprites[23][1] if len(env_sprites) > 23 and len(env_sprites[23]) > 1 else None,
        "purple": env_sprites[23][2] if len(env_sprites) > 23 and len(env_sprites[23]) > 2 else None,
    },
    "bookshelf": {
        "full": env_sprites[23][3] if len(env_sprites) > 23 and len(env_sprites[23]) > 3 else None,
        "empty": env_sprites[23][4] if len(env_sprites) > 23 and len(env_sprites[23]) > 4 else None
    },
    "trap-doo": { # Typo in original: trap-doo -> trapdoor
        "closed": env_sprites[22][0] if len(env_sprites) > 22 and len(env_sprites[22]) > 0 else None,
        "open": env_sprites[22][1] if len(env_sprites) > 22 and len(env_sprites[22]) > 1 else None,
    },
    "door": {
        "closed": env_sprites[22][2] if len(env_sprites) > 22 and len(env_sprites[22]) > 2 else None,
        "open": env_sprites[22][3] if len(env_sprites) > 22 and len(env_sprites[22]) > 3 else None,
    },
    "stool": env_sprites[23][5] if len(env_sprites) > 23 and len(env_sprites[23]) > 5 else None,
    "table": {
        "small": env_sprites[23][6] if len(env_sprites) > 23 and len(env_sprites[23]) > 6 else None,
        "big": env_sprites[23][7] if len(env_sprites) > 23 and len(env_sprites[23]) > 7 else None,
    },
    "radio": env_sprites[24][0] if len(env_sprites) > 24 and len(env_sprites[24]) > 0 else None,
    "night-stand": env_sprites[24][1] if len(env_sprites) > 24 and len(env_sprites[24]) > 1 else None,
    "toilet": env_sprites[24][2] if len(env_sprites) > 24 and len(env_sprites[24]) > 2 else None,
    "pot": {
        "empty": env_sprites[24][3] if len(env_sprites) > 24 and len(env_sprites[24]) > 3 else None,
        "green": env_sprites[24][4] if len(env_sprites) > 24 and len(env_sprites[24]) > 4 else None,
        "pink": env_sprites[24][5] if len(env_sprites) > 24 and len(env_sprites[24]) > 5 else None,
        "red": env_sprites[24][6] if len(env_sprites) > 24 and len(env_sprites[24]) > 6 else None,
    },
    "chest": env_sprites[24][7] if len(env_sprites) > 24 and len(env_sprites[24]) > 7 else None,
    "chair": {
        "empty": env_sprites[25][0] if len(env_sprites) > 25 and len(env_sprites[25]) > 0 else None,
        "red": env_sprites[25][1] if len(env_sprites) > 25 and len(env_sprites[25]) > 1 else None,
        "blue": env_sprites[25][2] if len(env_sprites) > 25 and len(env_sprites[25]) > 2 else None,
        "purple": env_sprites[25][3] if len(env_sprites) > 25 and len(env_sprites[25]) > 3 else None,
    },
    "bin": env_sprites[25][4] if len(env_sprites) > 25 and len(env_sprites[25]) > 4 else None,
    "modern_bin": env_sprites[25][4] if len(env_sprites) > 25 and len(env_sprites[25]) > 4 else None, # Same as bin
    "carpet": {
        "up": env_sprites[26][1] if len(env_sprites) > 26 and len(env_sprites[26]) > 1 else None,
        "middle": env_sprites[26][2] if len(env_sprites) > 26 and len(env_sprites[26]) > 2 else None,
        "down": env_sprites[26][3] if len(env_sprites) > 26 and len(env_sprites[26]) > 3 else None,
    },
    "oven": env_sprites[26][4] if len(env_sprites) > 26 and len(env_sprites[26]) > 4 else None,
}

# --- Fix for floor carpets (existing logic) ---
for color_i, color in enumerate(["red", "blue", "purple"]):
    map_for_carpet = {} # Use a distinct name for the map within the loop
    color_i *= 6

    for row, side in enumerate(["top", "middle", "bottom"]):
        for col, direction in enumerate(["left", "center", "right"]):
            base_row_index = color_i + row
            base_col_index = col
            if base_row_index < len(env_sprites) and base_col_index < len(env_sprites[base_row_index]):
                map_for_carpet[side + "_" + direction] = {
                    "without_middle": env_sprites[base_row_index][base_col_index],
                    "with_middle": env_sprites[base_row_index][base_col_index + 3] if base_col_index + 3 < len(env_sprites[base_row_index]) else None,
                    "without_border": env_sprites[base_row_index + 3][base_col_index] if base_row_index + 3 < len(env_sprites) and base_col_index < len(env_sprites[base_row_index + 3]) else None,
                }
            else:
                map_for_carpet[side + "_" + direction] = {
                    "without_middle": None, "with_middle": None, "without_border": None
                }

    # Add bounds checks for these specific indices too
    if (color_i + 3 < len(env_sprites) and 3 < len(env_sprites[color_i + 3])):
        map_for_carpet["top_right_left"] = env_sprites[color_i + 3][3]
    else: map_for_carpet["top_right_left"] = None

    if (color_i + 4 < len(env_sprites) and 3 < len(env_sprites[color_i + 4])):
        map_for_carpet["right_left"] = env_sprites[color_i + 4][3]
    else: map_for_carpet["right_left"] = None

    if (color_i + 5 < len(env_sprites) and 3 < len(env_sprites[color_i + 5])):
        map_for_carpet["bottom_right_left"] = env_sprites[color_i + 5][3]
    else: map_for_carpet["bottom_right_left"] = None

    if (color_i + 5 < len(env_sprites) and 4 < len(env_sprites[color_i + 5])):
        map_for_carpet["top_bottom_left"] = env_sprites[color_i + 5][4]
    else: map_for_carpet["top_bottom_left"] = None

    if (color_i + 5 < len(env_sprites) and 5 < len(env_sprites[color_i + 5])):
        map_for_carpet["top_bottom"] = env_sprites[color_i + 5][5]
    else: map_for_carpet["top_bottom"] = None

    if (color_i + 5 < len(env_sprites) and 6 < len(env_sprites[color_i + 5])):
        map_for_carpet["top_bottom_right"] = env_sprites[color_i + 5][6]
    else: map_for_carpet["top_bottom_right"] = None

    if (color_i + 5 < len(env_sprites) and 7 < len(env_sprites[color_i + 5])):
        map_for_carpet["top_bottom_right_left"] = env_sprites[color_i + 5][7]
    else: map_for_carpet["top_bottom_right_left"] = None

    sprite_map[color + "_carpet"] = map_for_carpet # Assign to sprite_map


# --- Fix top wall black strips (existing logic) ---
# Ensure these sprites are not None before accessing them
if sprite_map["wall"]["top"] is not None and sprite_map["wall"]["front"] is not None and \
   sprite_map["picture"] is not None and sprite_map["window"] is not None:

    w = scale(sprite_map["wall"]["top"]).get_width()
    WALL_PADDING = 7
    for y in range(config.square_size):
        for x in range(WALL_PADDING):
            sprite_map["wall"]["top"].set_at(
                (x, y), sprite_map["wall"]["top"].get_at((WALL_PADDING, y))
            )
            sprite_map["wall"]["top"].set_at(
                (w - 1 - x, y), sprite_map["wall"]["top"].get_at((w - WALL_PADDING - 2, y))
            )
            sprite_map["wall"]["front"].set_at(
                (x, y), sprite_map["wall"]["front"].get_at((WALL_PADDING, y))
            )
            sprite_map["wall"]["front"].set_at(
                (w - 1 - x, y),
                sprite_map["wall"]["front"].get_at((w - WALL_PADDING - 2, y)),
            )

    for x in range(w):
        for y in range(WALL_PADDING):
            c = sprite_map["wall"]["front"].get_at((x, 0))
            sprite_map["picture"].set_at((x, y), c)
            sprite_map["window"].set_at((x, y), c)

# Quit pygame's temporary display after all sprites are loaded
pygame.display.quit()
pygame.quit() # Final quit