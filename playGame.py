# playGame.py
# Matthew Nielsen, Section H, mqn

from basics import *
import random

################################################################################
### StarshipCommando (main game) Class
################################################################################

class StarshipCommando(Animation):
    
    ### user inputs ###
    
    def keyPressed(self, event):
        self.startTimerFired()
        # 6 lasers is the maximum allowed on the screen at a time
        if ((event.keysym == "space") and (len(self.playerLasers) < 6)):
            self.playerLasers[Laser.getLaserCount()] = Laser(self,
            self.playerX, self.playerY)
        # quit the game
        elif (event.keysym == "q"):
            StarshipCommando.highScores += [self.score]
            StarshipCommando.highScores.sort()
            StarshipCommando.highScores.reverse()
            self.init()
        # pause the game
        elif (event.keysym == "p"):
            self.stopTimerFired()
        # record arrow keys as being pressed
        elif (event.keysym not in self.pressedKeys):
            self.pressedKeys.append(event.keysym)
    
    def keyReleased(self, event):
        # remove keys that have been released from pressedKeys list
        if (event.keysym in self.pressedKeys):
            self.pressedKeys.remove(event.keysym)
    
    def keyExecuter(self):
        # execute all keys that have been pressed
        if (self.gameOver == False):
            for key in self.pressedKeys:
                if (key == "Up"):
                    self.changePlayerLocation(0, -self.playerSpeed)
                elif (key == "Down"):
                    self.changePlayerLocation(0, +self.playerSpeed)
                elif (key == "Left"):
                    self.changePlayerLocation(-self.playerSpeed, 0)
                elif (key == "Right"):
                    self.changePlayerLocation(+self.playerSpeed, 0)
    
    ### general game functions ###
    
    # splash screen helper functions
    
    def playGame(self):
        self.level = "play"
        self.startTimerFired()
    
    def easyMode(self):
        self.difficulty = "easy"
        self.startTimerFired()
    
    def mediumMode(self):
        self.difficulty = "medium"
        self.startTimerFired()
    
    def hardMode(self):
        self.difficulty = "hard"
        self.startTimerFired()
            
    def isLegalMove(self, x, y, dX, dY, width, height):
        newX = x + dX
        newY = y + dY
        # do not allow the player to go off the screen
        if ((newX < 0) or (newX + width >= self.canvasWidth) or
            (newY < 0 + self.statusHeight) or
            (newY + height >= self.canvasHeight)):
            return False
        return True
    
    def changePlayerLocation(self, dX, dY):
        # if the move is legal, adjust the player's (x, y) value
        if (self.isLegalMove(self.playerX, self.playerY, dX, dY, self.shipWidth,
            self.shipHeight) == True):
            self.playerX += dX
            self.playerY += dY
    
    def respawn(self):
        # called when the player is killed, re-place the player
        self.playerShields = 0
        self.playerX = 20
        self.playerY = (self.canvasHeight / 2) - self.shipHeight
    
    def generateShields(self):
        # randomly place shield upgrades on the screen
        if (random.randint(0, self.shieldsAmount) == True):
            self.shieldsNum += 1
            x, y = self.location()
            self.shields[self.shieldsNum] = (x, y)
    
    def generateEnemy(self):
        # randomply place enemy ships on the screen
        if (random.randint(0, self.enemyAmount) == True):
                x, y = self.location()
                self.enemies[Enemy.getEnemyCount()] = Enemy(self, x, y)
    
    def location(self):
        # finds a random location that does not touch the terrain
        x = self.canvasWidth
        while True:
            y = random.randint(self.statusHeight,
                               self.canvasHeight - self.shipHeight)
            if (self.terrain.impactsTerrain(self.shipWidth,
                                            self.shipHeight, x, y) == False):
                break
        return (x, y)
    
    ### timerFired ###
    
    def timerFired(self):
        self.keyExecuter()
        self.timeCount += 1
        if ((self.gameOver == False) and (self.win == False)):
            # initialize game values when the splash screen exits
            if (self.timeCount == 2):
                self.initTerrain()
                self.initEnemies()
                self.initPlayer()
            # do not randomly generate elements when fighting the boss
            if (self.level != "boss"):
                self.generateEnemy()
                self.generateShields()
            elif (self.level == "boss"):
                self.bossTimerFired()
            # when there is no terrain left, it is time to fight the boss
            if (self.terrain.getFrameCount() >= self.gameLength):
                self.level = "boss"
            # if the player hits the terrain, remove a life
            if (self.terrain.impactsTerrain(self.shipWidth, self.shipHeight,
                self.playerX, self.playerY)):
                if (self.playerLives == 1):
                    self.gameOver = True
                else:
                    self.playerLives -= 1
                    self.respawn()
            if (len(self.playerLasers) > 0):
                self.playerLaserTimerFired()
            if (len(self.enemies) > 0):
                self.enemyTimerFired()
            if ((len(self.playerLasers) > 0) and (len(self.enemies) > 0)):
                self.laserHitTimerFired()
            if (len(self.enemyLasers) > 0):
                self.enemyLaserTimerFired()
            if (len(self.shields) > 0):
                self.shieldsTimerFired()
    
    def bossTimerFired(self):
        removeLaser = None
        # check if the player's lasers are hitting the boss
        for laser in self.playerLasers:
            if (self.playerLasers[laser].isHit(self.boss.x,
                self.boss.y, self.bossWidth, self.bossHeight) == True):
                removeLaser = laser
                self.score += 100
                # decrease the boss' health
                if (self.bossHealth == 1):
                    self.score += 10000
                    self.win = True
                else:
                    self.bossHealth -= 1
        # remove lasers that hit the boss
        if (removeLaser != None):
            del self.playerLasers[removeLaser]
        # randomly make the boss shoot lasers
        if (self.boss.shootsLaser() == True):
            self.enemyLasers[Laser.getLaserCount()] = Laser(self,
            self.boss.x - self.bossWidth, self.boss.y)
        # move the boss into fighting position
        if (self.boss.x > self.canvasWidth / 1.5):
            self.boss.x -= self.enemySpeed
        # move the boss down until it hits the terrain, then change direction
        if (self.terrain.impactsTerrain(self.bossWidth,
            self.bossHeight, self.boss.x, self.boss.y) == True):
            self.bossMoveDir = 1
        # detect if the player hits the boss
        if (self.boss.hitsPlayer(self.playerX, self.playerY, self.bossWidth,
            self.bossHeight, self.shipWidth, self.shipHeight) == True):
            if (self.playerLives == 1):
                self.gameOver = True
            else:
                self.playerLives -= 1
                self.respawn()
        # move the boss up and down
        elif (self.boss.y < self.statusHeight):
            self.bossMoveDir = 0
        if (self.bossMoveDir == 1):
            self.boss.y -= self.enemySpeed
        else:
            self.boss.y += self.enemySpeed
    
    def playerLaserTimerFired(self):
        tempLasers = self.playerLasers
        self.playerLasers = dict()
        # move the player's lasers as long as they are on the screen
        for laser in tempLasers:
            if (tempLasers[laser].isLegalLaser(self.laserSpeed, tempLasers)
                == True):
                tempLasers[laser].x += self.laserSpeed
                self.playerLasers[laser] = tempLasers[laser]
    
    def enemyTimerFired(self):
        for enemy in self.enemies:
            # move enemies across the screen
            enemyXTemp = self.enemies[enemy].x
            enemyXTemp -= self.enemySpeed
            self.enemies[enemy].x = enemyXTemp
            # detect if the player hits an enemy
            if (self.enemies[enemy].hitsPlayer(self.playerX, self.playerY,
                self.shipWidth, self.shipHeight, self.shipWidth,
                self.shipHeight) == True):
                if (self.playerLives == 1):
                    self.gameOver = True
                else:
                    self.playerLives -= 1
                    self.respawn()
            # randomly make enemies shoot lasers
            if (self.enemies[enemy].shootsLaser() == True):
                self.enemyLasers[Laser.getLaserCount()] = Laser(self,
                self.enemies[enemy].x - self.shipWidth,
                self.enemies[enemy].y)
                
    def laserHitTimerFired(self):
        removeLaser = None
        removeEnemy = None
        # detect if any of the player's lasers hits an enemy
        for laser in self.playerLasers:
            for enemy in self.enemies:
                if (self.playerLasers[laser].isHit(self.enemies[enemy].x,
                    self.enemies[enemy].y, self.shipWidth,
                    self.shipHeight) == True):
                    removeLaser = laser
                    removeEnemy = enemy
                    self.score += 100
        # remove lasers that hit enemies
        if ((removeLaser != None) and (removeEnemy != None)):
            del self.playerLasers[removeLaser]
            del self.enemies[removeEnemy]
    
    def enemyLaserTimerFired(self):
        removeLaser = None
        # detect if any enemy lasers hits the player
        for laser in self.enemyLasers:
            if laser in self.enemyLasers:
                if (self.enemyLasers[laser].isHit(self.playerX,
                    self.playerY, self.shipWidth, self.shipHeight)
                    == True):
                    removeLaser = laser
                    # if a hit occurs, deal damage
                    if ((self.playerLives == 1) and (self.playerShields == 0)):
                        self.gameOver = True
                    elif (self.playerShields == 0):
                        self.playerLives -= 1
                        self.respawn()
                    else:
                        self.playerShields -= 1
                else:
                    # move enemy lasers until they go off the screen
                    tempLasers = self.enemyLasers
                    self.enemyLasers = dict()
                    for laser in tempLasers:
                        if (tempLasers[laser].isLegalLaser(self.laserSpeed,
                            tempLasers) == True):
                            tempLasers[laser].x -= self.laserSpeed
                            self.enemyLasers[laser] = tempLasers[laser]
        if (removeLaser != None):
            del self.enemyLasers[removeLaser]
    
    def shieldsTimerFired(self):
        removeShield = None
        # detect if the player picks up a shield upgrade
        for shield in self.shields:
            x, y = self.shields[shield]
            self.shields[shield] = (x - 5, y)
            if (((x <= self.playerX <= x + self.shipWidth) or
                (x <= self.playerX + self.shipWidth <= x + self.shipWidth)) and
                ((y <= self.playerY <= y + self.shipHeight) or
                (y <= self.playerY + self.shipHeight <= y + self.shipHeight))):
                if (self.playerShields < 6):
                    self.playerShields += 1
                    removeShield = shield
        if (removeShield != None):
            del self.shields[removeShield]
        
    ### drawing the game ###
    
    def redrawAll(self):
        self.canvas.delete(ALL)
        # draw the splash screen
        if (self.level == "splash"):
            self.drawSplashScreen()
        else:
            # draw all other elements of the game
            self.drawBackground()
            self.drawStatusBar()
            self.terrain.drawTerrainOnScreen()
            self.drawPlayer()
            if (self.level == "boss"):
                self.boss.drawBoss()
            if (Laser.getLaserCount() > 0):
                for laser in self.playerLasers:
                    self.playerLasers[laser].drawLaser()
            if (Enemy.getEnemyCount() > 0):
                for enemy in self.enemies:
                    self.enemies[enemy].drawEnemy()
            if (len(self.enemyLasers) > 0):
                for laser in self.enemyLasers:
                    self.enemyLasers[laser].drawLaser()
            if (len(self.shields) > 0):
                for shield in self.shields:
                    x, y = self.shields[shield]
                    self.drawShields(x, y)
            if (self.gameOver == True):
                self.drawGameOver()
            if (self.win == True):
                self.drawWin()
    
    def drawPlayer(self):
        # place the player's ship image on the screen and draw player shields
        self.canvas.create_image(self.playerX, self.playerY,
                                 anchor = NW, image = self.playerImage)
        self.canvas.create_rectangle(self.playerX - 5, self.playerY - 5,
                                     self.shipWidth + self.playerX + 5,
                                     self.shipHeight + self.playerY + 5,
                                     width = self.playerShields,
                                     outline = "cadet blue")
    
    def drawShields(self, x, y):
        # place shield upgrade images on the screen
        self.canvas.create_image(x, y, anchor = NW,
                                 image = self.shieldImage)
    
    def drawBackground(self):
        # place the space background image on the screen
        self.canvas.create_image(self.canvasWidth, self.canvasHeight,
                                 anchor = SE, image = self.background)
    
    def drawGameOver(self):
        # draw game over text
        cx = self.canvasWidth / 2
        cy = self.canvasHeight / 2
        self.canvas.create_text(cx, cy, text = "Game Over!",
                                font = ("Silom", 64), fill = "white")
        self.canvas.create_text(cx, cy + 64,
                                text = "Press 'q' to continue...",
                                font = ("Silom", 28), fill = "white")
    
    def drawWin(self):
        # draw win text
        cx = self.canvasWidth / 2
        cy = self.canvasHeight / 2
        self.canvas.create_text(cx, cy, text = "You Win!",
                                font = ("Silom", 64), fill = "white")
        self.canvas.create_text(cx, cy + 64,
                                text = "Press 'q' to continue...",
                                font = ("Silom", 28), fill = "white")
    
    def drawSplashScreen(self):
        self.stopTimerFired()
        # draw buttons
        self.canvas.create_window(320, 420, window = self.playButton)
        self.canvas.create_window(320, 230, window = self.easyButton)
        self.canvas.create_window(320, 270, window = self.mediumButton)
        self.canvas.create_window(320, 310, window = self.hardButton)
        # draw the red background
        self.canvas.create_rectangle(0, 0, self.canvasWidth,
                                     self.canvasHeight, fill = "red",
                                     width = 0)
        # draw the list of high scores
        self.canvas.create_text(104, 106, text = "High Scores:",
                                font = ("Silom", 28))
        if (len(StarshipCommando.highScores) > 0):
            for i in xrange(len(StarshipCommando.highScores)):
                self.canvas.create_text(104, 124 + (i + 1) * 24,
                text = str(StarshipCommando.highScores[i]),
                font = ("Silom", 18))
        # draw the difficulty setting choice
        self.canvas.create_text(320, 106, text = "Difficulty:",
                                font = ("Silom", 28))
        self.canvas.create_text(320, 146, text = self.difficulty,
                                font = ("Silom", 28))
        # draw the game's title from an image
        self.canvas.create_image(0, 0, anchor = NW, image = self.titleImage)
        # draw the game's instructions from an image
        self.canvas.create_image(420, 80, anchor = NW,
                                 image = self.instructions)
    
    def drawStatusBar(self):
        # create the status bar's background
        self.canvas.create_rectangle(0, 0, self.canvasWidth,
                                     self.statusHeight, fill = "white",
                                     width = 0)
        # draw the player's remaining lives
        for i in xrange(self.playerLives):
            self.canvas.create_image(200 + i * 32, 5, anchor = NW,
                                     image = self.livesImage)
        # draw the player's score
        self.canvas.create_text(5, 5, text = "Score: " + str(self.score),
                                font = ("Helvetica", 20, "bold"),
                                anchor = NW)
        # draw the player's shield level
        self.canvas.create_text(300, 5, text = "Shields: ",
                                font = ("Helvetica", 20, "bold"), anchor = NW)
        self.canvas.create_rectangle(380, 5, 380 + self.playerShields * 10, 28,
                                     fill = "blue", width = 0)
        # draw the boss' health bar
        if (self.level == "boss"):
            self.canvas.create_text(450, 5, text = "Boss: ",
                                    font = ("Helvetica", 20, "bold"),
                                    anchor = NW)
            self.canvas.create_rectangle(510, 5, 500 + self.bossHealth * 5, 28,
                                         fill = "red", width = 0)
        
    ### initialize the game ###
    
    def init(self):
        # init all game values
        self.initGameValues()
        self.initCanvasValues()
        self.initTerrain()
        self.initEnemies()
        self.initPlayer()
        self.initSplashScreen()
    
    def initGameValues(self):
        self.level = "splash"
        self.difficulty = "easy"
        self.timeCount = 0
        self.pressedKeys = []
        self.shields = dict()
        self.shieldsNum = 0
        self.laserSpeed = 15
        self.gameOver = False
        self.win = False
        self.timerDelay = 50
    
    def initCanvasValues(self):
        self.canvasWidth = 640
        self.canvasHeight = 480
        self.statusHeight = 32
        self.shipWidth = 64
        self.shipHeight = 64
        self.background = PhotoImage(file = "images/space.gif")
        self.livesImage = PhotoImage(file = "images/life.gif")
        self.shieldImage = PhotoImage(file = "images/shields.gif")
    
    def initTerrain(self):
        if (self.difficulty == "easy"):
            self.bottomBound = 380
            self.topBound = 320
        elif (self.difficulty == "medium"):
            self.bottomBound = 420
            self.topBound = 280
        elif (self.difficulty == "hard"):
            self.bottomBound = 460
            self.topBound = 240
        self.gameLength = 6000
        self.terrain = Terrain(self)
    
    def initEnemies(self):
        self.enemyImage = PhotoImage(file = "images/enemy.gif")
        self.bossImage = PhotoImage(file = "images/boss.gif")
        self.enemies = dict()
        self.enemyLasers = dict()
        self.lastEnemy = 0
        self.bossWidth = self.shipWidth * 2
        self.bossHeight = self.shipHeight * 2
        self.enemySpeed = 5
        if (self.difficulty == "easy"):
            self.enemyAmount = 50
            self.laserFreq = 50
            self.bossHealth = 10
        elif (self.difficulty == "medium"):
            self.enemyAmount = 40
            self.laserFreq = 40
            self.bossHealth = 15
        elif (self.difficulty == "hard"):
            self.enemyAmount = 30
            self.laserFreq = 30
            self.bossHealth = 20
        self.boss = Boss(self)
        self.bossMoveDir = 0
    
    def initPlayer(self):
        self.playerX = 20
        self.playerY = (self.canvasHeight / 2) - self.shipHeight
        self.playerSpeed = 5
        self.playerLasers = dict()
        if (self.difficulty == "easy"):
            self.shieldsAmount = 100
            self.playerLives = 3
        elif (self.difficulty == "medium"):
            self.shieldsAmount = 200
            self.playerLives = 2
        elif (self.difficulty == "hard"):
            self.shieldsAmount = 300
            self.playerLives = 1
        self.playerShields = 0
        self.playerImage = PhotoImage(file = "images/player.gif")
        self.score = 0
    
    def initSplashScreen(self):
        self.titleImage = PhotoImage(file = "images/title.gif")
        self.instructions = PhotoImage(file = "images/instructions.gif")
        self.playButton = Button(self.canvas, text = "Play!",
                                 command = self.playGame)
        self.easyButton = Button(self.canvas, text = "Easy",
                                 command = self.easyMode)
        self.mediumButton = Button(self.canvas, text = "Medium",
                                 command = self.mediumMode)
        self.hardButton = Button(self.canvas, text = "Hard",
                                 command = self.hardMode)
    
    highScores = []
        
################################################################################
### Laser Class
################################################################################

class Laser(StarshipCommando):
    
    laserCount = 0
    
    def __init__(self, StarshipCommando, x, y):
        # initialize values
        Laser.laserCount += 1
        self.canvas = StarshipCommando.canvas
        self.canvasHeight = StarshipCommando.canvasHeight
        self.canvasWidth = StarshipCommando.canvasWidth
        self.statusHeight = StarshipCommando.statusHeight
        self.shipWidth = StarshipCommando.shipWidth
        self.shipHeight = StarshipCommando.shipHeight
        self.speed = StarshipCommando.laserSpeed
        self.x = x + StarshipCommando.shipWidth
        self.y = y + StarshipCommando.shipHeight / 2
        self.width = 30
        self.height = 5
    
    @classmethod
    def getLaserCount(cls):
        # return how many lasers have been shot
        return Laser.laserCount
    
    def isLegalLaser(self, speed, allLasers):
        # determine if the laser is still on the screen
        if (self.isLegalMove(self.x, self.y, speed, 0, self.width,
            self.height) == True):
            return True
        else:
            return False
    
    def isHit(self, x, y, shipWidth, shipHeight):
        # determine if the laser hits a ship
        if (((x <= self.x <= x + shipWidth) or
             (x <= self.x + self.width <= x + shipWidth)) and
            ((y <= self.y <= y + shipHeight) or
             (y <= self.y + self.height <= y + shipHeight))):
            return True
        
    def drawLaser(self):
        # draw a green oval to represent a laser
        self.canvas.create_oval(self.x, self.y, self.x + self.width,
                                self.y + self.height, fill = "green", width = 0)

################################################################################
### Enemy Class
################################################################################

class Enemy(StarshipCommando):
    
    enemyCount = 0
    
    def __init__(self, StarshipCommando, x, y):
        # initialize values
        Enemy.enemyCount += 1
        self.canvasWidth = StarshipCommando.canvasWidth
        self.canvasHeight = StarshipCommando.canvasHeight
        self.statusHeight = StarshipCommando.statusHeight
        self.enemyImage = StarshipCommando.enemyImage
        self.canvas = StarshipCommando.canvas
        self.playerX = StarshipCommando.playerX
        self.playerY = StarshipCommando.playerY
        self.shipWidth = StarshipCommando.shipWidth
        self.shipHeight = StarshipCommando.shipHeight
        self.terrain = StarshipCommando.terrain
        self.topBound = StarshipCommando.topBound
        self.x, self.y = x, y
        self.laserFreq = StarshipCommando.laserFreq
        self.allEnemies = StarshipCommando.enemies
    
    @classmethod
    def getEnemyCount(cls):
        # return how many enemies have been created
        return Enemy.enemyCount
        
    def enemyLocation(self):
        # determine a random location for the enemy to spawn
        x = self.canvasWidth
        while True:
            y = random.randint(self.statusHeight,
                               self.topBound - self.shipHeight)
            for enemy in self.allEnemies:
                if not ((y <= enemy.y <= y + self.shipWidth) and
                    (y <= enemy.y + self.shipWidth <= y + self.shipWidth)):
                    break
        return (x, y)
    
    def hitsPlayer(self, playerX, playerY, enemyWidth, enemyHeight, playerWidth,
                   playerHeight):
        # determine if the enemy hits the player
        if (((self.x <= playerX <= self.x + enemyWidth) or
            (self.x <= playerX + playerWidth <= self.x + enemyWidth)) and
            ((self.y <= playerY <= self.y + enemyHeight) or
            (self.y <= playerY + playerHeight <= self.y + enemyHeight))):
            return True
    
    def shootsLaser(self):
        # randomly shoot lasers
        return random.randint(0, self.laserFreq)
     
    def drawEnemy(self):
        # place the enemy ship image on the screen
        self.canvas.create_image(self.x, self.y, anchor = NW,
                                 image = self.enemyImage)

################################################################################
### Boss Class
################################################################################

class Boss(Enemy):

    def __init__(self, StarshipCommando):
        # initialize values
        self.canvasWidth = StarshipCommando.canvasWidth
        self.canvasHeight = StarshipCommando.canvasHeight
        self.canvas = StarshipCommando.canvas
        self.bossImage = StarshipCommando.bossImage
        self.shipWidth = StarshipCommando.shipWidth
        self.shipHeight = StarshipCommando.shipHeight
        self.bossWidth = StarshipCommando.bossWidth
        self.bossHeight = StarshipCommando.bossHeight
        self.terrain = StarshipCommando.terrain
        self.topBound = StarshipCommando.topBound
        self.x = self.canvasWidth
        self.y = (self.canvasHeight / 2) - self.bossHeight        
        self.laserFreq = StarshipCommando.laserFreq
    
    def drawBoss(self):
        # place the boss image on the screen
        self.canvas.create_image(self.x, self.y, anchor = NW,
                                 image = self.bossImage)

################################################################################
### Terrain Class
################################################################################
    
class Terrain(StarshipCommando):
    
    def __init__(self, StarshipCommando):
        # initialize values
        self.canvas = StarshipCommando.canvas
        self.canvasWidth = StarshipCommando.canvasWidth
        self.canvasHeight = StarshipCommando.canvasHeight
        self.timeCount = StarshipCommando.timeCount
        self.gameLength = StarshipCommando.gameLength
        self.frameCount = 0
        self.startX = 0
        self.endX = StarshipCommando.gameLength
        self.spaceX = 5
        self.rangeY = 20
        self.startY = 400
        self.bottomBound = StarshipCommando.bottomBound
        self.topBound = StarshipCommando.topBound
        self.terrain = self.generate()
        self.terrainOnScreen = self.terrain[self.startX:self.canvasWidth]
    
    def getFrameCount(self):
        # return the frame of terrain currently being displayed
        return self.frameCount * self.spaceX + self.canvasWidth
        
    def generate(self):
        # randomly generate terrain
        points = [(self.startX, self.canvasHeight)]
        # x values are evenly spaced, but y values are a random variation on
        # the point previously created
        for x in xrange(self.startX, self.endX + self.spaceX, self.spaceX):
            y = random.randint(min(self.startY - self.rangeY, self.bottomBound),
                               max(self.startY + self.rangeY, self.topBound))
            self.startY = y
            points += [(x, y)]
        return points + [(self.endX, self.canvasHeight)]
    
    def impactsTerrain(self, shipWidth, shipHeight, playerX, playerY):
        # detect if the player hits the terrain
        for i in xrange(len(self.terrainOnScreen)):
            (x, y) = self.terrainOnScreen[i]
            if (((x <= playerX <= x + shipWidth) or 
                (x <= playerX + shipWidth <= x + shipWidth)) and
                ((y <= playerY) or (y <= playerY + shipHeight))):
                return True
        return False
    
    def drawTerrainOnScreen(self):
        # draw only the points of the terrain that the player will see using
        # the frame count as a reference
        self.terrainOnScreen = (self.terrain[self.frameCount:(self.frameCount + 
                                self.canvasWidth / self.spaceX) + 1])
        # give the points being displayed x values relative to the screen
        for i in xrange(len(self.terrainOnScreen)):
            (x, y) = self.terrainOnScreen[i]
            self.terrainOnScreen[i] = (i * self.spaceX, y)
        # draw a polygon containing those points
        self.canvas.create_polygon([(self.startX, self.canvasHeight)] +
                                   self.terrainOnScreen + [(self.canvasWidth,
                                   self.canvasHeight)], fill = "brown4")
        # if there is more terrain to draw, increase the frame count
        if (self.frameCount * self.spaceX + self.canvasWidth < self.gameLength):
            self.frameCount += 1
        
# run the game
game = StarshipCommando()
game.run()
