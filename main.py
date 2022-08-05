# -----------------------------------------imports and definitions--------------------------------------------
import pygame
# from pygame.locals import * : KCB originally not commented
from pygame import mixer  # KB pygame module for audio
import pickle  # KB pickle is an in-built Python module for serializing and deserializing object structures
from os import path  # KB operating system module

# game variables
gameLoop = 0  # KB variable to control the main game loop
score = 0
blockSize = 40  # KB2
mainMenu = True
level = 6
maxLevel = 6
gameOver = 0

# screen size
screenWidth = 800  # KB1
screenHeight = 800  # KB1

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()  # KB initialises pygame mixer
pygame.init()  # KB initialise pygame

clock = pygame.time.Clock()  # KB creates an object to help track time
fps = 60  # KB set frames per second to 60 fps

screen = pygame.display.set_mode((screenWidth, screenHeight))  # KB creates game window
pygame.display.set_caption('Platformer')  # KB names game window 'Platformer'

# game fonts
# font = pygame.font.SysFont('Arial', 50)
font1 = pygame.font.SysFont('Comic Sans MS', 50)
fontScore = pygame.font.SysFont('Comic Sans MS', 30)

# game colours
red = (255, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
blue = (0, 0, 255)

# load in music and sfx
pygame.mixer.music.load('images/Girl_from_Petaluma.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.5)
coinFx = pygame.mixer.Sound('img/coin.wav')
coinFx.set_volume(0.5)  # KB reduces volume by a half
jumpFx = pygame.mixer.Sound('img/jump.wav')
jumpFx.set_volume(0.5)
gameOverFx = pygame.mixer.Sound('img/game_over.wav')
gameOverFx.set_volume(0.5)

# load in pictures
bgImg = pygame.image.load('images/bluebg.jpg')
bgImg = pygame.transform.scale(bgImg, (800, 800))
restartImg = pygame.image.load('img/restart_btn.png')
startImg = pygame.image.load('images/playbut.png')
startImg = pygame.transform.scale(startImg, (300, 150))
exitImg = pygame.image.load('images/quitbut.png')
exitImg = pygame.transform.scale(exitImg, (300, 150))

# -------------------------------------------function-------------------------------------------------------

"""
def draw_grid():  # KB creates a 20x20 square grid on the game window
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * blockSize), (screenWidth, line * blockSize))
        pygame.draw.line(screen, (255, 255, 255), (line * blockSize, 0), (line * blockSize, screenHeight))
"""


def drawText(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# function that resets the level
def resetLevel(level):
    if level == 5:
        user1.reset(100, screenHeight - 670)
    else:
        user1.reset(100, screenHeight - 130)
    blobs.empty()
    lavas.empty()
    exits.empty()

    # load in level data and create world
    if path.exists(f'level{level}_data'):
        pickleIn = open(f'level{level}_data', 'rb')
        worldData = pickle.load(pickleIn)
    world = World(worldData)

    return world

# -----------------------------------------------classes-------------------------------------------------


class Button:
    def __init__(self, image, x, y):
        self.clicked = False
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        action = False
        # gets position of mouse
        pos = pygame.mouse.get_pos()

        # check mouse collisions and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                if self.clicked is False:
                    action = True
                    self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # create button
        screen.blit(self.image, self.rect)
        
        # function return
        return action


class User1:  # KCB orig code class User1():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, gameOver):
        walkCooldown = 5  # KB limits speed of user1 walking animation
        dy = 0  # KB variable for user1's change in y
        dx = 0  # KB variable for user1's change in x

        match gameOver:
            case 0:
                # get key presses
                key = pygame.key.get_pressed()
                if key[pygame.K_LEFT]:  # KB user1 moves left on left key pressed
                    dx -= 5
                    self.counter += 1  # KB switches between user1 sprite images to create animation
                    self.direction = -1  # KB detects change in direction
                if key[pygame.K_RIGHT]:  # KB user1 moves right on right key pressed
                    dx += 5
                    self.counter += 1  # KB switches between user1 sprite images to create animation
                    self.direction = 1  # KB detects change in direction
                if key[pygame.K_SPACE]:
                    if self.jumped is False:
                        if self.inAir is False:
                            jumpFx.play()
                            self.velY = -15
                            self.jumped = True
                if key[pygame.K_SPACE] is False:  # KCB orig : if key[pygame.K_SPACE] == False:
                    self.jumped = False
                if key[pygame.K_LEFT] is False:
                    if key[pygame.K_RIGHT] is False:
                        self.counter = 0
                        self.index = 0
                        if self.direction == 1:  # KB when user1 is stationary it will face previous direction traversed
                            self.image = self.imagesRight[self.index]
                        if self.direction == -1:  # KB when user1 is stationary it will face previous direction traversed
                            self.image = self.imagesLeft[self.index]

                # deal with the walking animation
                if self.counter > walkCooldown:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.imagesRight):
                        self.index = 0
                    match self.direction:
                        case 1:
                            self.image = self.imagesRight[self.index]
                        case -1:
                            self.image = self.imagesLeft[self.index]

                # mimic falling gravity
                self.velY += 1
                if self.velY > 10:
                    self.velY = 10
                dy += self.velY

                # collision checks
                self.inAir = True
                for block in world.blockList:
                    # check for horizontal collisions (x axis)
                    if block[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                        dx = 0  # KB sets character's change in x back to 0
                    # checks for vertical collisions (y axis)
                    if block[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                        # check if user1 is below blocks
                        if self.velY < 0:
                            dy = block[1].bottom - self.rect.top
                            self.velY = 0
                        # check if user1 is above blocks
                        elif self.velY >= 0:
                            dy = block[1].top - self.rect.bottom
                            self.velY = 0
                            self.inAir = False

                # check if user1 collided with blobs
                if pygame.sprite.spritecollide(self, blobs, False):
                    gameOver = -1
                    gameOverFx.play()

                # check if user1 collided with lava
                if pygame.sprite.spritecollide(self, lavas, False):
                    gameOver = -1
                    gameOverFx.play()

                # check if user1 collided with exit (gate)
                if pygame.sprite.spritecollide(self, exits, False):
                    gameOver = 1  # KB go to next level

                # update user1 coordinates
                self.rect.x += dx
                self.rect.y += dy

            case -1:  # KB changes user1 sprite to ghost upon dying
                self.image = self.deadImage
                drawText('GAME OVER', font1, white, (screenWidth // 2 - 150), screenHeight - 700)
                if self.rect.y > 200:  # KB causes the user1's soul to ascend
                    self.rect.y -= 5

        # draw user1
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # KB draws rectangle around user1

        return gameOver

    def reset(self, x,y):
        self.index = 0
        self.counter = 0
        self.imagesRight = []
        self.imagesLeft = []
        num = 1
        while num < 5:
            imgRight = pygame.image.load(f'images/sprite{num}.png')  # KB different user1 sprite moving appearance
            imgRight = pygame.transform.scale(imgRight, (32, 64))  # KB3 animate user1 moving right
            imgLeft = pygame.transform.flip(imgRight, True, False)  # KB animate user1 moving left
            self.imagesRight.append(imgRight)  # KB stores the four images of user1 moving right
            self.imagesLeft.append(imgLeft)  # KB stores the four images of user1 moving left
            num += 1
        self.deadImage = pygame.image.load('img/ghost.png')
        self.image = self.imagesRight[self.index]
        self.rect = self.image.get_rect()  # KB creates rectangle around user1
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.jumped = False
        self.inAir = True
        self.velY = 0
        self.direction = 0


class World:  # KCB orig code: class World():
    def __init__(self, data):
        self.blockList = []

        # load images
        dirtImg = pygame.image.load('images/dirtblock.png')
        grassImg = pygame.image.load('images/grassblock.png')

        rowCount = 0
        for row in data:
            colCount = 0
            for block in row:
                match block:
                    case 1:
                        img = pygame.transform.scale(dirtImg, (blockSize, blockSize))
                        imgRect = img.get_rect()  # KB creates a rectangle out of the image
                        imgRect.x = colCount * blockSize  # KB calculates the x coordinate of block rectangle on the screen
                        imgRect.y = rowCount * blockSize  # KB calculates the y coordinate of block rectangle on the screen
                        block = (img, imgRect)  # KB tuple that store the image and the position of the rectangle
                        self.blockList.append(block)  # KB adds the image and position (tuple) to the list
                    case 2:
                        img = pygame.transform.scale(grassImg, (blockSize, blockSize))
                        imgRect = img.get_rect()
                        imgRect.x = colCount * blockSize
                        imgRect.y = rowCount * blockSize
                        block = (img, imgRect)  # KB tuple that store the image and the position of the rectangle
                        self.blockList.append(block)
                    case 3:
                        blob = Enemy(colCount * blockSize, rowCount * blockSize + 15)
                        blobs.add(blob)
                    case 6:
                        lava = Lava(colCount * blockSize, rowCount * blockSize + (blockSize // 2))
                        lavas.add(lava)
                    case 7:
                        coin = Coin(colCount * blockSize + (blockSize // 2), rowCount * blockSize + (blockSize // 2))
                        coins.add(coin)
                    case 8:
                        exit = Exit(colCount * blockSize, rowCount * blockSize - (blockSize // 2))
                        exits.add(exit)
                colCount += 1
            rowCount += 1

    def draw(self):
        for block in self.blockList:
            screen.blit(block[0], block[1])
            pygame.draw.rect(screen, (255, 255, 255), block[1], 2)  # KB draws rectangle around each block


class Enemy(pygame.sprite.Sprite):  # KB uses pygame inbuilt sprite objects
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/ballboy.png')
        self.image = pygame.transform.scale(img, (48, 37.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moveDirection = 1  # KB variable used for enemy motion
        self.moveCounter = 0  # KB variable used control enemy movement direction

    def update(self):
        self.rect.x += self.moveDirection
        self.moveCounter += 1  # KB moves enemy by one pixel
        if abs(self.moveCounter) > 50:  # KB makes enemy move in opposite direction when enemy mvmnt exceeds 50 pixels
            self.moveDirection *= -1
            self.moveCounter *= -1
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # KB draws rectangle around blob enemy


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (blockSize, blockSize // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coin.png')
        self.image = pygame.transform.scale(img, (blockSize // 2, blockSize // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (blockSize, int(blockSize * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# KB initial layout of the screen with several images
# 1 is 'img/dirt.png';  2 is 'img/grass.png'

"""
worldData = [
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

# -----------------------------------------------create instances---------------------------------------------

if level == 5:
    user1 = User1(100, screenHeight - 670)
else:
    user1 = User1(100, screenHeight - 130)
#  user1 = User1(100, screenHeight - 130)

# create screen objects
blobs = pygame.sprite.Group()  # KB creates an instance of empty list of enemy sprites
lavas = pygame.sprite.Group()
coins = pygame.sprite.Group()
exits = pygame.sprite.Group()

# create coin icon for showing the score
scoreCoin = Coin(blockSize * 2.5, blockSize * 1.5)
coins.add(scoreCoin)

# load in level data and create world
if path.exists(f'level{level}_data'):
    pickleIn = open(f'level{level}_data', 'rb')
    worldData = pickle.load(pickleIn)
world = World(worldData)

# define buttons
startButton = Button(startImg, screenWidth // 2 - 350, screenHeight // 2)
exitButton = Button(exitImg, screenWidth // 2 + 50, screenHeight // 2)
restartButton = Button(restartImg, screenWidth // 2 - 50, screenHeight // 2 + 100)

# ------------------------------------------main game loop----------------------------------------

gameLoop = 0  # KB continue game

while gameLoop == 0:

    clock.tick(fps)  # KB let pygame control frame per second (fps)

    screen.blit(bgImg, (0, 0))

    if mainMenu:
        if exitButton.draw() is True:
            gameLoop = 1
        if startButton.draw() is True:
            mainMenu = False

    else:
        world.draw()  # KB calls draw method to create initial screen based on the world map

        if gameOver == 0:
            blobs.update()
            # score update
            if pygame.sprite.spritecollide(user1, coins, True):
                score += 1
                coinFx.play()
            drawText(str(score), fontScore, white, blockSize + 9, blockSize - 2)

        blobs.draw(screen)  # KB calls draw function for blob group
        
        lavas.draw(screen)  # KB calls draw function for lava group
        
        coins.draw(screen)  # KB calls draw function for coin group
        
        exits.draw(screen)  # KB calls draw function for exit group

        gameOver = user1.update(gameOver)

        # check if user1 died
        match gameOver:
            case -1:
                if restartButton.draw() is True:
                    score = 0
                    worldData = []
                    world = resetLevel(level)
                    gameOver = 0

            #  check if user1 has finished the level
            case 1:
                # progress to next level
                level += 1
                # reinit level
                if level <= maxLevel:
                    gameOver = 0
                    worldData = []
                    world = resetLevel(level)
                else:
                    drawText('WINNER!!', font1, yellow, (screenWidth // 2 - 115), screenHeight - 700)
                    if restartButton.draw() is True:
                        gameOver = 0
                        score = 0
                        level = 1
                        # reinit level
                        worldData = []
                        world = resetLevel(level)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameLoop = 1

    pygame.display.update()

pygame.quit()
