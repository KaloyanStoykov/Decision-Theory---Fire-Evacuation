import pygame
from envs.constants import config
import os  # Import os for path manipulation

# 8x28 is likely the dimension of the entire sprite sheet in terms of individual 16x16 sprites
# 128x432 is the pixel dimension of the sheet
ENV_SPRITE_ROWS = 27  # This seems correct for the "4 BigSet.png" if it's 16px sprites
ENV_SPRITE_COLS = 8
sprite_map = {}

# --- Helper functions ---


# Function to scale a single sprite to the config.square_size
def scale(sprite, size=-1):
    if sprite is None:
        return None

    if size == -1:  # this is required for dynamically setting the config
        size = config.square_size

    return pygame.transform.scale(sprite, (size, size))


# Function to load a sprite sheet and chop it into individual sprites
def load_sprite_sheet(filename, rows, cols, size):
    if not config.is_rendering:
        return [[None] * cols] * rows

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_rect = sheet.get_rect()

        sprites = []
        # Iterate through the sheet to extract subsurfaces
        for y_offset in range(rows):  # Use row index for cleaner loop
            if (
                y_offset * size > sheet_rect.height
            ):  # Check if we're trying to go beyond sheet height
                raise IndexError(
                    "Sheet is too small to fit the requested rows. Requested rows: "
                    + str(rows)
                    + ", sheet height: "
                    + str(sheet_rect.height)
                    + ", y_offset: "
                    + str(y_offset)
                )

            row_sprites = []
            for x_offset in range(cols):  # Use col index
                if (
                    x_offset * size > sheet_rect.width
                ):  # Check if we're trying to go beyond sheet width
                    raise IndexError(
                        "Sheet is too small to fit the requested columns. Requested columns: "
                        + str(cols)
                        + ", sheet width: "
                        + str(sheet_rect.width)
                        + ", x_offset: "
                        + str(x_offset)
                    )

                # Ensure the subsurface doesn't go out of bounds of the actual image
                sub_rect_x = x_offset * size
                sub_rect_y = y_offset * size
                sub_rect_width = min(size, sheet_rect.width - sub_rect_x)
                sub_rect_height = min(size, sheet_rect.height - sub_rect_y)

                if sub_rect_width > 0 and sub_rect_height > 0:
                    row_sprites.append(
                        sheet.subsurface(
                            pygame.Rect(
                                sub_rect_x, sub_rect_y, sub_rect_width, sub_rect_height
                            )
                        ).copy()
                    )
            if row_sprites:  # Only add if row has sprites
                sprites.append(row_sprites)
    except pygame.error as e:
        print(f"Error loading sprite sheet {filename}: {e}")
        sprites = []  # Return empty if error

    return sprites


# Function to load fire sprites specifically
def load_fire_sprites():
    if not config.is_rendering:
        return [None] * 4

    fires = []
    try:
        for i in range(1, 5):  # Assumes Fogo_1.png to Fogo_4.png
            filepath = os.path.join("assets", "Fogo_" + str(i) + ".png")
            sheet = pygame.image.load(filepath).convert_alpha()
            # These values (1024/28, 16, piece*4) suggest a specific internal layout of your fire images
            # If Fogo_*.png are individual frames of fire animation, they should be loaded differently.
            # Assuming these are sheets that contain a specific fire sprite
            piece = 1024 / 28
            offset = piece * 16  # This offset picks a specific part of the image
            frame = scale(
                sheet.subsurface(
                    pygame.Rect(offset, offset, piece * 4, piece * 4)
                ).copy()
            )
            fires.append(frame)
    except pygame.error as e:
        print(f"Error loading fire sprite Fogo_{i}.png: {e}")
        fires = []  # Return empty if error

    return fires


# --- Core sprite loading ---

# Load the main environment sprite sheet
# Pygame should only be initialized once for the main display loop.
# Initializing and quitting pygame multiple times in load_sprite_sheet/load_fire_sprites
# is generally bad practice and can lead to issues.
# Let's ensure Pygame is initialized only once for the entire script.

# Pygame initialization for the whole sprites.py file
# A temporary display surface is still needed for image loading

shadow_sheet = None


def fix_firefighter(sprite_100x100_sheet, with_shadow=True):
    if sprite_100x100_sheet is None:
        return None
    # This function expects a 100x100 sprite from the sheet and extracts a 24x24 sub-sprite
    # and recolors it.
    size = 24  # The actual size of the firefighter sprite within the 100x100 block
    x_offset_in_100 = (100 - size) // 2  # = 38 (instead of 42 based on (100-24)/2)
    y_offset_in_100 = (100 - size) // 2  # = 38

    # Use the actual size to ensure the rect is correct
    firefighter_sprite_cut = sprite_100x100_sheet.subsurface(
        pygame.Rect(x_offset_in_100, y_offset_in_100, size, size)
    ).copy()
    firefighter_sprite_scaled = scale(
        firefighter_sprite_cut
    )  # Scale to config.square_size

    def hex_to_rgba(hex_color):
        hex_color = hex_color.lstrip("#").lstrip("0x")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    colors_to_replace = [
        (hex_to_rgba(old), hex_to_rgba(new))
        for old, new in [
            ("#607581", "#672020"),  # Example color changes
            ("#C2CDD2", "#8F3838"),
            ("#9BADB7", "#672020"),
            ("#C5D0D5", "#8F3838"),
            ("#425C6B", "#561D1D"),
            ("#5D6C75", "#561D1D"),
            ("#6F828D", "#511D1D"),
            ("#7F909A", "#511D1D"),
            ("#7B4E16", "#B19E9A"),
            ("#8D6534", "#B19E9A"),
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
                    break  # Move to next pixel after replacement

    if with_shadow:
        # Load and process shadow
        # Ensure Soldier-Shadow.png is a 100x100 sprite as well if it's from a sheet
        if shadow_sheet and shadow_sheet[0]:
            raw_shadow = shadow_sheet[0][0]
            # Extract the same 24x24 sub-sprite and scale it
            shadow_cut = raw_shadow.subsurface(
                pygame.Rect(x_offset_in_100, y_offset_in_100, size, size)
            ).copy()
            shadow_scaled = scale(shadow_cut)
            shadow_scaled.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
            shadow_scaled.blit(
                firefighter_sprite_scaled, (0, 0)
            )  # Blit the colored sprite onto the shadow
            return shadow_scaled
        else:
            print(
                "Warning: Soldier-Shadow.png not loaded correctly. Returning firefighter without shadow."
            )
            return firefighter_sprite_scaled
    else:
        return firefighter_sprite_scaled


def fix_cat(sprite):
    return scale(sprite, config.square_size - 24)


def load_srpite_map():
    global sprite_map, shadow_sheet
    pygame.init()
    pygame.display.set_mode((1000, 1000), pygame.HIDDEN)
    shadow_sheet = load_sprite_sheet("assets/Soldier-Shadow.png", 1, 1, 100)

    env_sprites = [
        [scale(sprite) for sprite in sprite_list]
        for sprite_list in load_sprite_sheet(
            "assets/4 BigSet.png", ENV_SPRITE_ROWS, ENV_SPRITE_COLS, 16
        )
    ]

    map = {
        "fires": load_fire_sprites(),
        "firefighter": {
            "idle": [
                fix_firefighter(sprite)
                for sprite in load_sprite_sheet("assets/Soldier-Idle.png", 1, 6, 100)[0]
            ],
            "dying": [
                fix_firefighter(sprite)
                for sprite in (
                    load_sprite_sheet("assets/Soldier-Hurt.png", 1, 3, 100)[0]
                    + load_sprite_sheet("assets/Soldier-Death.png", 1, 4, 100)[0]
                )
            ],
            "put_out_fire": [
                fix_firefighter(sprite, False)
                for sprite in load_sprite_sheet(
                    "assets/Soldier-Attack01_Effect.png", 1, 6, 100
                )[0][3:5]
            ],
        },
        "cat": [
            fix_cat(sprite)
            for sprite in load_sprite_sheet("assets/cat.png", 1, 4, 32)[0]
        ],
        "wall": {
            "front": env_sprites[20][3],
            "top": env_sprites[19][3],
            "half": env_sprites[21][3],
        },
        "floor_tile": env_sprites[19][1],
        "window": env_sprites[21][6],
        "picture": env_sprites[21][7],
        "bed": {
            "red": env_sprites[23][0],
            "blue": env_sprites[23][1],
            "purple": env_sprites[23][2],
        },
        "bookshelf": {"full": env_sprites[23][3], "empty": env_sprites[23][4]},
        "trap-doo": {
            "closed": env_sprites[22][0],
            "open": env_sprites[22][1],
        },
        "door": {
            "closed": env_sprites[22][2],
            "open": env_sprites[22][3],
        },
        "stool": env_sprites[23][5],
        "table": {
            "small": env_sprites[23][6],
            "big": env_sprites[23][7],
        },
        "radio": env_sprites[24][0],
        "night-stand": env_sprites[24][1],
        "toilet": env_sprites[24][2],
        "pot": {
            "empty": env_sprites[24][3],
            "green": env_sprites[24][4],
            "pink": env_sprites[24][5],
            "red": env_sprites[24][6],
        },
        "chest": env_sprites[24][7],
        "chair": {
            "red": env_sprites[25][2],
            "blue": env_sprites[25][2],
            "purple": env_sprites[25][3],
        },
        "bin": env_sprites[25][4],
        "modern_bin": env_sprites[25][4],
        "carpet": {
            "up": env_sprites[26][1],
            "middle": env_sprites[26][2],
            "down": env_sprites[26][3],
        },
        "oven": env_sprites[26][4],
        "controlls": {
            "a": scale(pygame.image.load("assets/a.svg").convert_alpha(), 20),
            "w": scale(pygame.image.load("assets/w.svg").convert_alpha(), 20),
            "d": scale(pygame.image.load("assets/d.svg").convert_alpha(), 20),
            "s": scale(pygame.image.load("assets/s.svg").convert_alpha(), 20),
            "u": scale(pygame.image.load("assets/u.svg").convert_alpha(), 20),
            "l": scale(pygame.image.load("assets/l.svg").convert_alpha(), 20),
            "down": scale(pygame.image.load("assets/down.svg").convert_alpha(), 20),
            "r": scale(pygame.image.load("assets/r.svg").convert_alpha(), 20),
            "space": pygame.transform.scale(
                pygame.image.load("assets/space.svg").convert_alpha(), (40, 30)
            ),
        },
    }

    sprite_map.update(map)

    for color_i, color in enumerate(["red", "blue", "purple"]):
        map = {}
        color_i *= 6

        # order is top, bottom, right, left
        for row, side in enumerate(["top", "middle", "bottom"]):
            for col, direction in enumerate(["left", "center", "right"]):
                map[side + "_" + direction] = {
                    "without_middle": env_sprites[color_i + row][col],
                    "with_middle": env_sprites[color_i + row][col + 3],
                    "without_border": env_sprites[color_i + row + 3][col],
                }

        map["top_right_left"] = env_sprites[color_i + 3][3]
        map["right_left"] = env_sprites[color_i + 4][3]
        map["bottom_right_left"] = env_sprites[color_i + 5][3]

        map["top_bottom_left"] = env_sprites[color_i + 5][4]
        map["top_bottom"] = env_sprites[color_i + 5][5]
        map["top_bottom_right"] = env_sprites[color_i + 5][6]

        map["top_bottom_right_left"] = env_sprites[color_i + 5][7]

        sprite_map[color + "_carpet"] = map

    if not config.is_rendering:
        return

    # fix top wall black strips
    w = scale(sprite_map["wall"]["top"]).get_width()
    WA = 7
    for y in range(config.square_size):
        for x in range(WA):
            sprite_map["wall"]["top"].set_at(
                (x, y), sprite_map["wall"]["top"].get_at((WA, y))
            )
            sprite_map["wall"]["top"].set_at(
                (w - 1 - x, y),
                sprite_map["wall"]["top"].get_at((w - WA - 6, y)),
            )
            sprite_map["wall"]["front"].set_at(
                (x, y), sprite_map["wall"]["front"].get_at((WA, y))
            )
            sprite_map["wall"]["front"].set_at(
                (w - 1 - x, y),
                sprite_map["wall"]["front"].get_at((w - WA - 6, y)),
            )

    for x in range(w):
        for y in range(WA):
            c = sprite_map["wall"]["front"].get_at((x, 0))
            sprite_map["picture"].set_at((x, y), c)
            sprite_map["window"].set_at((x, y), c)

    pygame.quit()
