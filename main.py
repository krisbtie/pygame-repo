import pygame
# from pygame.locals import * : KCB originally not commented
from pygame import mixer  # KB pygame module for audio
import pickle  # KB pickle is an in-built Python module for serializing and deserializing object structures
from os import path  # KB operating system module

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()  # KB initialises pygame mixer
pygame.init()  # KB initialise pygame

clock = pygame.time.Clock()  # KB creates an object to help track time
fps = 60  # KB set frames per second to 60 fps

screenWidth = 800  # KB1
screenHeight = 800  # KB1

screen = pygame.display.set_mode((screenWidth, screenHeight))  # KB creates game window
pygame.display.set_caption('Platformer')  # KB names game window 'Platformer'

# define game variables
tileSize = 40  # KB2
game_over = 0
main_menu = True
level = 1
max_levels = 7

# load images
# sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('images/bluebg.jpg')
bg_img = pygame.transform.scale(bg_img, (800, 800))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('images/playbut.png')
start_img = pygame.transform.scale(start_img, (300, 150))
exit_img = pygame.image.load('images/quitbut.png')
exit_img = pygame.transform.scale(exit_img, (300, 150))


# load sounds
# pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.load('images/Girl_from_Petaluma.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.5)
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)  # KB reduces volume by a half
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)


"""
def draw_grid():  # KB creates a 20x20 square grid on the game window
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tileSize), (screenWidth, line * tileSize))
        pygame.draw.line(screen, (255, 255, 255), (line * tileSize, 0), (line * tileSize, screenHeight))
"""


# function that resets the level
def reset_level(level):
    if level == 5:
        player.reset(100, screenHeight - 670)
    else:
        player.reset(100, screenHeight - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    # load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # gets position of mouse
        pos = pygame.mouse.get_pos()

        # check mouse collisions and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)

        return action


class Player:  # KCB orig code class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0  # KB variable for player's change in x
        dy = 0  # KB variable for player's change in y
        walk_cooldown = 5  # KB limits speed of player animation

        if game_over == 0:
            # get key presses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped is False and self.in_air is False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] is False:  # KCB orig : if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:  # KB player moves left on left key pressed
                dx -= 5
                self.counter += 1  # KB switches between player sprite images to create animation
                self.direction = -1  # KB detects change in direction
            if key[pygame.K_RIGHT]:  # KB player moves right on right key pressed
                dx += 5
                self.counter += 1  # KB switches between player sprite images to create animation
                self.direction = 1  # KB detects change in direction
            if key[pygame.K_LEFT] is False and key[pygame.K_RIGHT] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:  # KB when player is stationary it will face previous direction traversed
                    self.image = self.images_right[self.index]
                if self.direction == -1:  # KB when player is stationary it will face previous direction traversed
                    self.image = self.images_left[self.index]

            # handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:  # KB changes player sprite to face right
                    self.image = self.images_right[self.index]
                if self.direction == -1:  # KB changes player sprite to face left
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0  # KB sets character's change in x back to 0
                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground i.e. falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check if player collided with enemies
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game_over_fx.play()

            # check if player collided with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:  # KB changes player sprite to ghost upon dying
            self.image = self.dead_image
            if self.rect.y > 200:  # KB causes the player's soul to ascend
                self.rect.y -= 5

        # draw player onto screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # KB draws rectangle around player

        return game_over

    def reset(self, x,y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):  # KB num 1, 2, 3, 4
            img_right = pygame.image.load(f'img/guy{num}.png')  # KB different player sprite moving appearance
            img_right = pygame.transform.scale(img_right, (32, 64))  # KB3 animate player moving right
            img_left = pygame.transform.flip(img_right, True, False)  # KB animate player moving left
            self.images_right.append(img_right)  # KB stores the four images of player moving right
            self.images_left.append(img_left)  # KB stores the four images of player moving left
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()  # KB creates rectangle around player
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World:  # KCB orig code: class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        dirt_img = pygame.image.load('images/dirtblock.png')
        grass_img = pygame.image.load('images/grassblock.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tileSize, tileSize))
                    img_rect = img.get_rect()  # KB creates a rectangle out of the image
                    img_rect.x = col_count * tileSize  # KB calculates the x coordinate of tile rectangle on the screen
                    img_rect.y = row_count * tileSize  # KB calculates the y coordinate of tile rectangle on the screen
                    tile = (img, img_rect)  # KB tuple that store the image and the position of the rectangle
                    self.tile_list.append(tile)  # KB adds the image and position (tuple) to the list
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tileSize, tileSize))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tileSize
                    img_rect.y = row_count * tileSize
                    tile = (img, img_rect)  # KB tuple that store the image and the position of the rectangle
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tileSize, row_count * tileSize + 15)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tileSize, row_count * tileSize + (tileSize // 2))
                    lava_group.add(lava)
                if tile == 8:
                    exit = Exit(col_count * tileSize, row_count * tileSize - (tileSize // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)  # KB draws rectangle around each tile


class Enemy(pygame.sprite.Sprite):  # KB uses pygame inbuilt sprite objects
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1  # KB variable used for enemy motion
        self.move_counter = 0  # KB variable used control enemy movement direction

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1  # KB moves enemy by one pixel
        if abs(self.move_counter) > 50:  # KB makes enemy move in opposite direction when enemy mvmnt exceeds 50 pixels
            self.move_direction *= -1
            self.move_counter *= -1
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tileSize, tileSize // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tileSize, int(tileSize * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# KB initial layout of the screen with several images
# 1 is 'img/dirt.png';  2 is 'img/grass.png'
"""
world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
    [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
    [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]
"""

# KB creates instances
if level == 5:
    player = Player(100, screenHeight - 670)
else:
    player = Player(100, screenHeight - 130)
#  player = Player(100, screenHeight - 130)

blob_group = pygame.sprite.Group()  # KB creates an instance of empty list of enemy sprites
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# create buttons
restart_button = Button(screenWidth // 2 - 50, screenHeight // 2 + 100, restart_img)
start_button = Button(screenWidth // 2 - 350, screenHeight // 2, start_img)
exit_button = Button(screenWidth // 2 + 50, screenHeight // 2, exit_img)

# KB game loop
run = True
while run:

    clock.tick(fps)  # KB let pygame control frame per second (fps)

    screen.blit(bg_img, (0, 0))
    # screen.blit(sun_img, (100, 100))

    if main_menu is True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    else:
        world.draw()  # KB calls draw method to create initial screen based on the world map

        if game_over == 0:
            blob_group.update()

        blob_group.draw(screen)  # KB calls draw function for blob group
        lava_group.draw(screen)  # KB calls draw function for lava group
        exit_group.draw(screen)  # KB calls draw function for exit group

        game_over = player.update(game_over)

        # if player has died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        #  if player has completed the level
        if game_over == 1:
            # reset game and go to next level
            level += 1
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                    # reset level
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
