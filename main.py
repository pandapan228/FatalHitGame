import pygame
import sys
import os

pygame.init()
WIDTH, HEIGHT = 1130, 700
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
    fon = pygame.transform.scale(fon0, (1130, 700))
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


wall_image = load_image('data/wall1.jpg')
player_image = load_image('data/player_sprite3.png')

tile_width = tile_height = 75


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
left_group = pygame.sprite.Group()
right_group = pygame.sprite.Group()
gun_group = pygame.sprite.Group()


class Left(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(left_group, all_sprites)
        self.image = wall_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Right(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(right_group, all_sprites)
        self.image = wall_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = wall_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


class Mob(pygame.sprite.Sprite):
    pass


class Gun(pygame.sprite.Sprite):
    pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            pos_x * tile_width + 15, pos_y * tile_height + 5)
        self.pos = pos_x, pos_y
        self.left = False
        self.right = True
        self.count = 0

    def update(self):
        if not pygame.sprite.spritecollideany(self, tiles_group):
            self.rect = self.rect.move(0, 10)
        if self.left:
            if self.count % 2 == 0:
                self.image = load_image('data/player_sprite33.png')
            else:
                self.image = load_image('data/player_sprite22.png')

        if self.right:
            if self.count % 2 == 0:
                self.image = load_image('data/player_sprite3.png')
            else:
                self.image = load_image('data/player_sprite2.png')


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '%':
                Left(x, y)
            elif level[y][x] == '*':
                Right(x, y)
            elif level[y][x] == '#':
                Wall(x, y)
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
            if not pygame.sprite.spritecollideany(player, left_group):
                if event.key == pygame.K_LEFT:
                    player.left = True
                    player.right = False
                    player.count += 1
                    player.rect = player.rect.move(-30, 0)
            else:
                player.rect = player.rect.move(10, 0)
            if not pygame.sprite.spritecollideany(player, right_group):
                if event.key == pygame.K_RIGHT:
                    player.right = True
                    player.left = False
                    player.count += 1
                    player.rect = player.rect.move(30, 0)
            else:
                player.rect = player.rect.move(-10, 0)
            if event.key == pygame.K_SPACE:
                if pygame.sprite.spritecollideany(player, tiles_group):
                    player.rect = player.rect.move(0, -200)

    make_fon('data/fon2.png')
    player_group.update()
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)


end_screen()
terminate()