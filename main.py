import pygame
import sys
import os

pygame.init()
WIDTH, HEIGHT = 1000, 700
FPS = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    if not os.path.isfile(name):
        print('Файл не найден')
        sys.exit()
    image = pygame.image.load(name)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image.convert_alpha()
    return image


def make_fon(name):
    fon0 = load_image(name)
    fon = pygame.transform.scale(fon0, (1000, 700))
    screen.blit(fon, (0, 0))


def greeting():
    make_fon('data/dungeon_greeting.png')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


greeting()


def load_level(filename):
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


tile_images = {
    'wall': load_image('data/wall1.jpg')
}
player_image = load_image('data/player_static.png')

tile_width = tile_height = 75


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = pos_x, pos_y
        self.moving = False
        self.falling = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT
                        or event.key == pygame.K_RIGHT
                        or event.key == pygame.K_SPACE):
                    self.moving = True
                    self.falling = True
        if self.moving:
            self.image = AnimatedSprite(load_image('player_sprite.png'), 8, 2, 50, 50)
            self.moving = False
        if self.falling:
            while y > 0 and level_map[y - 1][x] == '.':
                player.pos = x, y + 1
                player.rect = player.image.get_rect().move(tile_width * player.pos[0] + 15,
                                                           tile_height * player.pos[1] + 5)
            self.falling = False


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y)
                level[y][x] = '.'
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


level_map = load_level('data/map.txt')
player, level_x, level_y = generate_level(level_map)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            x, y = player.pos
            if event.key == pygame.K_LEFT:
                if x > 0 and level_map[y][x - 1] == '.':
                    player.pos = x - 1, y
                    player.rect = player.image.get_rect().move(tile_width * player.pos[0] + 15,
                                                               tile_height * player.pos[1] + 5)
            elif event.key == pygame.K_RIGHT:
                if x < level_x and level_map[y][x + 1] == '.':
                    player.pos = x + 1, y
                    player.rect = player.image.get_rect().move(tile_width * player.pos[0] + 15,
                                                               tile_height * player.pos[1] + 5)
            elif event.key == pygame.K_SPACE:
                if y > 0 and level_map[y - 1][x] == '.':
                    player.pos = x, y - 1
                    player.rect = player.image.get_rect().move(tile_width * player.pos[0] + 15,
                                                               tile_height * player.pos[1] + 5)

    make_fon('data/fon2.png')
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)


end_screen()
terminate()