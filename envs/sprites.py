import pygame

# 8x28
# 128x432
SPRITE_SIZE = 16
ROWS = 27
COLS = 8
PADDING = 6

def load_sprite_sheet(filename, sprite_width, sprite_height):
    pygame.init()
    pygame.display.set_mode((128 + COLS * PADDING + PADDING, 432 + ROWS * PADDING + PADDING))

    sheet = pygame.image.load(filename).convert_alpha()
    sheet_rect = sheet.get_rect()

    sprites = []
    for y in range(0, sheet_rect.height, sprite_height):
        if y + sprite_height > sheet_rect.height:
            continue
        
        row = []
        for x in range(0, sheet_rect.width, sprite_width):
            if x + sprite_width > sheet_rect.width:
                continue
            
            frame = sheet.subsurface(pygame.Rect(x, y, sprite_width, sprite_height)).copy()
            row.append(frame)
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
        frame = sheet.subsurface(pygame.Rect(offset, offset, piece * 4, piece * 4)).copy()
        fires.append(frame)

    pygame.quit()
    return fires
    
sprites = load_sprite_sheet("assets/4 BigSet.png", SPRITE_SIZE, SPRITE_SIZE)

def display_sheet():
    pygame.init()
    screen = pygame.display.set_mode((128 + COLS * PADDING + PADDING, 432 + ROWS * PADDING + PADDING))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        tile_size = SPRITE_SIZE + PADDING # space between sprites (padding)

        for row in range(ROWS):
            for col in range(COLS):
                x = PADDING + col * tile_size
                y = PADDING + row * tile_size
                screen.blit(sprites[row][col], (x, y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def test_sprite(sprite):
    pygame.init()
    screen = pygame.display.set_mode(( 2 * PADDING + SPRITE_SIZE, 2 * PADDING + SPRITE_SIZE))
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

sprite_map = {
    "fires": load_fire_sprites(),
    "wall": {
        "front": sprites[20][3],
        "top": sprites[19][3],
        "half": sprites[21][3],
    },
    "floor_tile": sprites[19][1],
    "window": sprites[21][6],
    "picture": sprites[21][7],
    "bed": {
        "red": sprites[23][0],
        "blue": sprites[23][1],
        "purple": sprites[23][2]
    },
    "bookshelf": {
        "full": sprites[23][3],
        "empty": sprites[23][4]
    },
    "trap-doo": {
        "closed": sprites[22][0],
        "open": sprites[22][1],
    },
    "door": {
        "closed": sprites[22][2],
        "open": sprites[22][3],
    },
    "stool": sprites[23][5],
    "table": {
        "small": sprites[23][6],
        "big": sprites[23][7],
    },
    "radio": sprites[24][0],
    "night-stand": sprites[24][1],
    "toilet": sprites[24][2],
    "pot": {
        "empty": sprites[24][3],
        "green": sprites[24][4],
        "pink": sprites[24][5],
        "red": sprites[24][6],
    },
    "chest": sprites[24][7],
    "chair": {
        "empty": sprites[25][0],
        "red": sprites[25][1],
        "blue": sprites[25][2],
        "purple": sprites[25][3]
    },
    "bin": sprites[25][3],
    "modern_bin": sprites[25][4],
    "carpet": {
        "up": sprites[26][1],
        "middle": sprites[26][2],
        "down": sprites[26][3]
    },
    "oven": sprites[26][4]
}

for color_i, color in enumerate(["red", "blue", "purple"]):
  map = {}
  color_i *= 6
  
  # order is top, bottom, right, left
  for row, side in enumerate(["top", "middle", "bottom"]):
    for col, direction in enumerate(["left", "center", "right"]):
      map[side + "_" + direction] = {
        "without_middle": sprites[color_i + row][col],
        "with_middle": sprites[color_i + row][col + 3],
        "without_border": sprites[color_i + row + 3][col],
      }
  
  map["top_right_left"] = sprites[color_i + 3][3]
  map["right_left"] = sprites[color_i + 4][3]
  map["bottom_right_left"] = sprites[color_i + 5][3]

  map["top_bottom_left"] = sprites[color_i + 5][4]
  map["top_bottom"] = sprites[color_i + 5][5]
  map["top_bottom_right"] = sprites[color_i + 5][6]

  map["top_bottom_right_left"] = sprites[color_i + 5][7]
  
  sprite_map[color + "_carpet"] = map

# fix top wall black strips
w = sprite_map["wall"]["top"].get_width()
for y in range(sprite_map["wall"]["top"].get_height()):
    sprite_map["wall"]["top"].set_at((0, y), sprite_map["wall"]["top"].get_at((1, y)))
    sprite_map["wall"]["top"].set_at((w-1, y), sprite_map["wall"]["top"].get_at((w-2, y)))
    sprite_map["wall"]["front"].set_at((0, y), sprite_map["wall"]["front"].get_at((1, y)))
    sprite_map["wall"]["front"].set_at((w-1, y), sprite_map["wall"]["front"].get_at((w-2, y)))

for x in range(w):
    c = sprite_map["picture"].get_at((x, 1))
    sprite_map["picture"].set_at((x, 0), c)
    sprite_map["window"].set_at((x, 0), c)

if __name__ == "__main__":
    # test_sprite(sprite_map["window"])
    display_sheet()