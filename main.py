import pygame
import sys
import os
from random import choice, randrange


pygame.init()
WIDTH, HEIGHT = 1130, 700
FPS = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
LOBBY_MUSIC = pygame.mixer.Sound('data/lobby_music.mp3')
GAME_MUSIC = pygame.mixer.Sound('data/game_music.mp3')
FINAL_MUSIC = pygame.mixer.Sound('data/final_music.mp3')


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
    global LOBBY_MUSIC
    make_fon('data/dungeon_greeting.png')
    LOBBY_MUSIC.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                LOBBY_MUSIC.stop()
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
gun_image = load_image('data/gun_sprite1.png')


tile_width = tile_height = 75


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
left_group = pygame.sprite.Group()
right_group = pygame.sprite.Group()
gun_group = pygame.sprite.Group()
mob_group = pygame.sprite.Group()


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


class Score:
    def __init__(self):
        self.kill_count = 0

    def add_kill(self):
        self.kill_count += 1

    def get_score(self):
        return self.kill_count


score = Score()


class Mob(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(mob_group, all_sprites)
        images1 = ['data/mob1.png', 'data/mob2.png', 'data/mob3.png']
        self.mob_image1 = load_image(choice(images1))
        images2 = ['data/mob11.png', 'data/mob22.png', 'data/mob33.png']
        self.mob_image2 = load_image(choice(images2))
        self.image = self.mob_image1
        self.count = 0
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        if not pygame.sprite.spritecollideany(self, tiles_group):
            self.rect = self.rect.move(0, 10)
        if self.rect.x >= 500:
            self.image = self.mob_image2
        else:
            self.image = self.mob_image1
        if pygame.sprite.spritecollideany(self, gun_group):
            self.kill()
            score.add_kill()


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(gun_group, all_sprites)
        self.image = gun_image
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        if not player.location:
            self.image = load_image('data/gun_sprite11.png')
            if (pygame.sprite.spritecollideany(self, left_group)
                    or pygame.sprite.spritecollideany(self, tiles_group)):
                self.kill()
            else:
                self.rect = self.rect.move(-50, 0)
        else:
            self.image = load_image('data/gun_sprite1.png')
            if (pygame.sprite.spritecollideany(self, right_group)
                    or pygame.sprite.spritecollideany(self, tiles_group)
                    or pygame.sprite.spritecollideany(self, mob_group)):
                self.kill()
            else:
                self.rect = self.rect.move(50, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            pos_x * tile_width + 15, pos_y * tile_height + 5)
        self.pos = pos_x, pos_y
        self.location = True
        self.count = 0

    def update(self):
        global GAME_MUSIC
        GAME_MUSIC.play(-1)
        if not pygame.sprite.spritecollideany(self, tiles_group):
            self.rect = self.rect.move(0, 10)
        if not self.location:
            if self.count % 2 == 0:
                self.image = load_image('data/player_sprite33.png')
            else:
                self.image = load_image('data/player_sprite22.png')

        else:
            if self.count % 2 == 0:
                self.image = load_image('data/player_sprite3.png')
            else:
                self.image = load_image('data/player_sprite2.png')
        if pygame.sprite.spritecollideany(self, mob_group):
            self.kill()
            GAME_MUSIC.stop()
            file = open('data/score.csv', mode='w')
            count = score.get_score()
            text = f'GAME SCORE: {count}'
            file.write(text)
            file.close()
            end_screen()
            terminate()


def end_screen():
    global FINAL_MUSIC
    make_fon('data/end_screen.png')
    FINAL_MUSIC.play(-1)
    ending_text = ['ИГРА ОКОНЧЕНА', ''
                   f'ВАШ СЧЁТ: {score.get_score()}']
    font = pygame.font.Font(None, 75)
    text_coord = 75
    for line in ending_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        ending_rect = string_rendered.get_rect()
        text_coord += 75
        ending_rect.top = text_coord
        ending_rect.x = 10
        text_coord += ending_rect.height
        screen.blit(string_rendered, ending_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                FINAL_MUSIC.stop()
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


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
        location = False
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            right = False
            left = False
            if not pygame.sprite.spritecollideany(player, left_group):
                if event.key == pygame.K_LEFT:
                    player.location = False
                    player.count += 1
                    player.rect = player.rect.move(-30, 0)
            else:
                player.rect = player.rect.move(10, 0)
            if not pygame.sprite.spritecollideany(player, right_group):
                if event.key == pygame.K_RIGHT:
                    player.location = True
                    player.count += 1
                    player.rect = player.rect.move(30, 0)
            else:
                player.rect = player.rect.move(-10, 0)
            if event.key == pygame.K_SPACE:
                if pygame.sprite.spritecollideany(player, tiles_group):
                    player.rect = player.rect.move(0, -200)
            if event.key == pygame.K_n:
                x = randrange(80, 990)
                ys = [80, 230, 380, 530]
                y = choice(ys)
                Mob(x, y)
                if player.location:
                    Gun(player.rect.x + 50, player.rect.y + 8)
                else:
                    Gun(player.rect.x - 28, player.rect.y + 8)

    make_fon('data/fon2.png')
    gun_group.update()
    mob_group.update()
    player_group.update()
    tiles_group.draw(screen)
    gun_group.draw(screen)
    mob_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
