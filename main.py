import pygame
# from pygame.locals import * : KCB originally not commented

pygame.init()  # KB initialise pygame

clock = pygame.time.Clock()  # KB creates an object to help track time
fps = 60  # KB set frames per second to 60 fps

screenWidth = 800  # KB1
screenHeight = 800  # KB1

screen = pygame.display.set_mode((screenWidth, screenHeight))  # KB creates game window
pygame.display.set_caption('Platformer')  # KB names game window 'Platformer'

# define game variables
tileSize = 40  # KB2

# load images
# sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('images/bluebg.jpg')
bg_img = pygame.transform.scale(bg_img, (800,800))


"""
def draw_grid():  # KB creates a 20x20 square grid on the game window
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tileSize), (screenWidth, line * tileSize))
        pygame.draw.line(screen, (255, 255, 255), (line * tileSize, 0), (line * tileSize, screenHeight))
"""


class Player:  # KCB orig code class Player():
    def __init__(self, x, y):
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
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()  # KB creates rectangle around player
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0

    def update(self):
        dx = 0  # KB variable for player's change in x
        dy = 0  # KB variable for player's change in y
        walk_cooldown = 5  # KB limits speed of player animation

        # get key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and self.jumped is False:  # KCB orig : if key[pygame.K_SPACE] and self.jumped == False:
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

        # update player coordinates
        self.rect.x += dx
        self.rect.y += dy

        if self.rect.bottom > screenHeight:  # stops player from falling off the screen
            self.rect.bottom = screenHeight
            dy = 0

        # draw player onto screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # KB draws rectangle around player


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


# KB initial layout of the screen with several images
# 1 is 'img/dirt.png';  2 is 'img/grass.png'
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

# KB creates instances
player = Player(100, screenHeight - 130)
blob_group = pygame.sprite.Group()  # KB creates an instance of empty list of enemy sprites
world = World(world_data)

# KB game loop
run = True
while run:

    clock.tick(fps)  # KB let pygame control frame per second (fps)

    screen.blit(bg_img, (0, 0))
    # screen.blit(sun_img, (100, 100))

    world.draw()  # KB calls draw method to create initial screen based on the world map

    blob_group.update()  # KB calls update method from Enemy object
    blob_group.draw(screen)  # KB calls draw method to draw enemies

    player.update()  # KB calls update method to put player on screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
