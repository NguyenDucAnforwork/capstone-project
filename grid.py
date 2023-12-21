from utility_functions import *


# Grid and Token classes definition
# do not touch this file, my man


class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size
        self.tile_size = self.size[0]
        self.whitetoken = loadImages('assets/WhiteToken.png', size)
        self.blacktoken = loadImages('assets/BlackToken.png', size)
        self.transitionWhiteToBlack = [loadImages(f'assets/WhiteToBlack{i}.png', self.size) for i in range(1, 4)]
        self.transitionBlackToWhite = [loadImages(f'assets/BlackToWhite{i}.png', self.size) for i in range(1, 4)]
        self.bg = self.loadBackGroundImages()

        self.tokens = {}

        self.gridBg = self.createbgimg()

        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0

        self.font = pygame.font.SysFont('Arial', self.tile_size // 4, True, False)

    def newGame(self):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j] + str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def createbgimg(self):
        t1, t2 = 'A0', 'B0'  # tile squares
        s1, s2, s3, s4 = 'D0', 'E1', 'D2', 'C1'  # side squares, clockwise
        c1, c2, c3, c4 = 'C0', 'E0', 'E2', 'C2'  # corner squares, clockwise
        gridBg = [
            [c1, s1, s1, s1, s1, s1, s1, s1, s1, c2],
            [s4, t1, t2, t1, t2, t1, t2, t1, t2, s2],
            [s4, t2, t1, t2, t1, t2, t1, t2, t1, s2],
            [s4, t1, t2, t1, t2, t1, t2, t1, t2, s2],
            [s4, t2, t1, t2, t1, t2, t1, t2, t1, s2],
            [s4, t1, t2, t1, t2, t1, t2, t1, t2, s2],
            [s4, t2, t1, t2, t1, t2, t1, t2, t1, s2],
            [s4, t1, t2, t1, t2, t1, t2, t1, t2, s2],
            [s4, t2, t1, t2, t1, t2, t1, t2, t1, s2],
            [c4, s3, s3, s3, s3, s3, s3, s3, s3, c3],
        ]
        image = pygame.Surface((self.tile_size * 12, self.tile_size * 12))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    def regenGrid(self, rows, columns):
        """generate an empty grid for logic use"""
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)
        self.insertToken(grid, -1, 3, 3)
        self.insertToken(grid, 1, 3, 4)
        self.insertToken(grid, -1, 4, 4)
        self.insertToken(grid, 1, 4, 3)

        return grid

    def calculatePlayerScore(self, player):
        score = 0
        for row in self.gridLogic:
            for col in row:
                if col == player:
                    score += 1
        return score

    def drawScore(self, player, score):
        textImg = self.font.render(f'{player} : {score}', 1, 'White')
        return textImg

    def endScreen(self):
        tile = self.tile_size
        if self.GAME.gameOver:
            endScreenImg = pygame.Surface((tile * 4, tile * 4))
            message = "Black Won!!" if self.player1Score > self.player2Score \
                else "White Won!!" if self.player1Score < self.player2Score \
                else "Tie!!"
            endText = self.font.render(message, 1, 'White')
            endScreenImg.blit(endText, (0, 0))
            newGame = pygame.draw.rect(endScreenImg, 'White',
                                       (tile, tile * 2, tile * 2, tile))
            newGameText = self.font.render('Play Again', 1, 'Black')
            endScreenImg.blit(newGameText, (tile * 1.5, tile * 2.375))
        return endScreenImg

    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))

        window.blit(self.drawScore('Black', self.player1Score), (self.tile_size * 11, self.tile_size))
        window.blit(self.drawScore('White', self.player2Score), (self.tile_size * 11, self.tile_size * 2))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == self.GAME.human_player:
            for move in availMoves:
                pygame.draw.rect(window, 'White',
                                 (self.tile_size + (move[1] * self.tile_size) + self.tile_size * (3 / 8),
                                  self.tile_size + (move[0] * self.tile_size) + self.tile_size * (3 / 8),
                                  self.tile_size / 4, self.tile_size / 4))

        if self.GAME.gameOver:
            window.blit(self.endScreen(), (self.tile_size * 3, self.tile_size * 3))

    def markRecentMove(self, window, move):
        if move is not None:
            pygame.draw.rect(window, 'Red',
                             (self.tile_size + (move[1] * self.tile_size) + self.tile_size * (3 / 8),
                              self.tile_size + (move[0] * self.tile_size) + self.tile_size * (3 / 8),
                              self.tile_size / 4, self.tile_size / 4))

    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    def findValidCells(self, grid, curPlayer):
        """Performs a check to find all empty cells that are adjacent to opposing player"""
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue

                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []

            RUN = True
            while RUN:
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles

    def findAvailMoves(self, grid, currentPlayer):
        """Takes the list of validCells and checks each to see if playable"""
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            # if len(swapTiles) > 0 and cell not in playableCells:
            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells

    def insertToken(self, grid, curplayer, y, x):
        tokenImage = self.blacktoken if curplayer == 1 else self.whitetoken
        self.tokens[(y, x)] = Token(curplayer, y, x, self.tile_size, tokenImage, self.GAME)
        grid[y][x] = self.tokens[(y, x)].player

    def animateTransitions(self, cell, player):
        if player == 1:
            self.tokens[(cell[0], cell[1])].transition(self.transitionWhiteToBlack, self.blacktoken)
        else:
            self.tokens[(cell[0], cell[1])].transition(self.transitionBlackToWhite, self.whitetoken)


class Token:
    def __init__(self, player, gridX, gridY, size, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = size + (gridY * size)
        self.posY = size + (gridX * size)
        self.GAME = main

        self.image = image

    def transition(self, transitionImages, tokenImage):
        for i in range(30):
            self.image = transitionImages[i // 10]
            self.GAME.draw()
        self.image = tokenImage

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))
