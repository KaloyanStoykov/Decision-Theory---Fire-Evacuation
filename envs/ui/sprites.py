import pygame
from envs.constants import config

# 8x28
# 128x432
ENV_SPRITE_ROWS = 27
ENV_SPRITE_COLS = 8
PADDING = 0


def scale(sprite, size=config.square_size):
    return pygame.transform.scale(sprite, (size, size))


def load_sprite_sheet(filename, rows, cols, size):
    pygame.init()
    pygame.display.set_mode(
        (
            cols * (size + PADDING) + PADDING,
            rows * (size + PADDING) + PADDING,
        )
    )

    sheet = pygame.image.load(filename).convert_alpha()
    sheet_rect = sheet.get_rect()

    sprites = []
    for y in range(0, sheet_rect.height, size):
        if y + size > sheet_rect.height:
            continue

        row = []
        for x in range(0, sheet_rect.width, size):
            if x + size > sheet_rect.width:
                continue

            row.append(sheet.subsurface(pygame.Rect(x, y, size, size)).copy())
        if row:
            sprites.append(row)

    pygame.quit()
    return sprites


def load_fire_sprites():
    fires = []
    pygame.init()
    pygame.display.set_mode((1024, 1024))
    for i in range(1, 5):
        sheet = pygame.image.load("assets/Fogo_" + str(i) + ".png").convert_alpha()
        piece = 1024 / 28
        offset = piece * 16
        frame = scale(
            sheet.subsurface(pygame.Rect(offset, offset, piece * 4, piece * 4)).copy()
        )
        fires.append(frame)

    pygame.quit()
    return fires


env_sprites = [
    [scale(sprite) for sprite in sprite_list]
    for sprite_list in load_sprite_sheet(
        "assets/4 BigSet.png", ENV_SPRITE_COLS, ENV_SPRITE_ROWS, 16
    )
]


def display_sheet(sprites, rows, cols):
    pygame.init()
    screen = pygame.display.set_mode(
        (
            cols * (PADDING + config.square_size) + PADDING,
            rows * (PADDING + config.square_size) + PADDING,
        )
    )
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        tile_size = config.square_size + PADDING  # space between sprites (padding)

        for row in range(rows):
            for col in range(cols):
                x = PADDING + col * tile_size
                y = PADDING + row * tile_size
                screen.blit(sprites[row][col], (x, y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def test_sprite(sprite, size):
    pygame.init()
    screen = pygame.display.set_mode((2 * PADDING + size, 2 * PADDING + size))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((40, 40, 40))
        screen.blit(sprite, (PADDING, PADDING))

        pygame.display.flip()
        clock.tick(160)

    pygame.quit()


def fix_firefighter(sprite, with_shadow=True):
    size = 24
    x = (100 - size) // 2  # = 42
    y = (100 - size) // 2  # = 42

    def hex_to_rgba(hex_color):
        hex_color = hex_color.lstrip("#").lstrip("0x")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    colors_to_replace = [
        (hex_to_rgba(old), hex_to_rgba(new))
        for old, new in [
            ("#607581", "#672020"),
            ("#C2CDD2", "#8F3838"),
            ("#9BADB7", "#672020"),
            ("#C5D0D5", "#8F3838"),
            ("#425C6B", "#561D1D"),
            ("#5D6C75", "#561D1D"),
            ("#6F828D", "#511D1D"),
            ("#7F909A", "#511D1D"),
            ("#7B4E16", "#B19E9A"),
            ("##8D6534", "#B19E9A"),
        ]
    ]

    firefigther = scale(sprite.subsurface(pygame.Rect(x, y, size, size)).copy())
    shadow = load_sprite_sheet("assets/Soldier-Shadow.png", 1, 1, 100)[0][0]
    shadow.fill((0, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)

    shadow = scale(shadow.subsurface(pygame.Rect(x, y, size, size)).copy())

    width, height = firefigther.get_size()
    for x in range(width):
        for y in range(height):
            for old_color, new_color in colors_to_replace:
                if firefigther.get_at((x, y)) == old_color:
                    firefigther.set_at((x, y), new_color)

    if not with_shadow:
        return firefigther

    shadow.blit(firefigther, (0, 0))

    return shadow


def fix_cat(sprite):
    PADDING = 34
    return scale(sprite, config.square_size - PADDING)


sprite_map = {
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
        fix_cat(sprite) for sprite in load_sprite_sheet("assets/cat.png", 1, 4, 32)[0]
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
        "empty": env_sprites[25][0],
        "red": env_sprites[25][1],
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
}

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

# fix top wall black strips
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
