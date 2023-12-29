import copy
import random
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

        self.tokens = {}

        self.sprite_image = 'assets/wood.png'
        self.tile_sprite = ('A0', 'B0')
        self.bg = self.loadBackGroundImages()
        self.gridBg = self.createbgimg()

        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0

        self.font = pygame.font.SysFont('Arial', int(self.tile_size // 4), True, False)

    def newGame(self, random_sprite):
        self.tokens.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)
        if random_sprite:
            self.sprite_image = random.choice(('assets/wood.png', 'assets/demo_spritesheet.png'))
            alpha = random.choice((('A', 'B'), ('F', 'G')))
            num = random.choice(range(3))
            self.tile_sprite = (f'{alpha[0] + str(num)}', f'{alpha[1] + str(num)}')
            self.bg = self.loadBackGroundImages()
            self.gridBg = self.createbgimg()

    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load(self.sprite_image).convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j] + str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict

    def createbgimg(self):
        t1, t2 = self.tile_sprite  # tile squares
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
        opening_library = [
            [[(0, 5), (1, 4), (2, 3), (2, 2), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)],
             [(2, 4), (3, 5), (4, 5), (5, 5)]],
            [[(2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6)],
             [(4, 3), (4, 4), (5, 2), (5, 3), (5, 4)]],
            [[(1, 2), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3), (3, 4), (4, 3), (5, 3)],
             [(1, 3), (2, 4), (3, 5), (4, 4), (4, 5)]],
            [[(1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (4, 3), (5, 4)],
             [(2, 5), (3, 4), (3, 5), (4, 4), (4, 5), (5, 3)]],
            [[(2, 1), (2, 2), (2, 3), (3, 4), (4, 2), (4, 3), (4, 4), (4, 5)],
             [(1, 3), (2, 4), (3, 1), (3, 2), (3, 3), (3, 5)]],
            [[(1, 4), (2, 3), (2, 4), (2, 5), (3, 4), (4, 2), (4, 3), (4, 4)],
             [(1, 3), (2, 2), (3, 1), (3, 2), (3, 3), (3, 5)]],
            [[(1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (4, 2), (5, 3), (6, 4)],
             [(2, 5), (3, 4), (3, 5), (4, 3), (4, 4), (4, 5)]],
            [[(2, 1), (2, 2), (2, 3), (3, 4), (4, 2), (4, 3), (4, 4), (4, 5)],
             [(1, 3), (2, 4), (3, 1), (3, 2), (3, 3), (3, 5)]],
            [[(1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (3, 5), (4, 2), (5, 1)],
             [(3, 4), (4, 1), (4, 3), (4, 4), (4, 5), (5, 3)]],
            [[(2, 2), (3, 2), (3, 3), (3, 5), (4, 2), (4, 3), (5, 3), (5, 4), (6, 3)],
             [(2, 3), (3, 4), (4, 4), (4, 5), (5, 2)]]
        ]
        random_opening = random.choice(range(0, len(opening_library)))
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)

        # for whiteToken in opening_library[random_opening][0]:
        #     self.insertToken(grid, 1, whiteToken[0], whiteToken[1])

        # for blackToken in opening_library[random_opening][1]:
        #     self.insertToken(grid, -1, blackToken[0], blackToken[1])

        self.insertToken(grid, -1, 3, 3)
        self.insertToken(grid, 1, 3, 4)
        self.insertToken(grid, -1, 4, 4)
        self.insertToken(grid, 1, 4, 3)

        return grid

    def recoverGrid(self, template):
        self.tokens.clear()
        self.gridLogic = copy.deepcopy(template)
        rows, cols = len(self.gridLogic), len(self.gridLogic[0])
        for y in range(rows):
            for x in range(cols):
                tile = self.gridLogic[y][x]
                if tile == 1:
                    self.tokens[(y, x)] = Token(1, y, x, self.tile_size, self.blacktoken, self.GAME)
                elif tile == -1:
                    self.tokens[(y, x)] = Token(-1, y, x, self.tile_size, self.whitetoken, self.GAME)

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

    def drawTurns(self, window):
        if self.GAME.mode == 0 and not self.GAME.gameOver:
            turn_text = f'Turn : {self.GAME.turn_count} / {self.GAME.data["turn_count"]}'
        else:
            turn_text = f'Turn : {self.GAME.turn_count}'
        text_img = self.font.render(turn_text, 1, 'White')
        window.blit(text_img, (self.tile_size * 11.2, self.tile_size * 3.5))

    def drawRollbackButton(self, window):
        tile = self.tile_size
        if self.GAME.human_player and self.GAME.mode != 0:
            pygame.draw.rect(window, 'White', (tile * 10.8, tile * 8, tile * 1.6, tile))
            textImg = self.font.render('Rollback', 1, 'Black')
            window.blit(textImg, (self.tile_size * 11.18, self.tile_size * 8.34))

    def drawBranchButton(self, window):
        tile = self.tile_size
        if self.GAME.mode == 0 and self.GAME.data['game_mode'] != 2:
            pygame.draw.rect(window, 'White', (tile * 10.8, tile * 8, tile * 1.6, tile))
            textImg = self.font.render('Branch', 1, 'Black')
            window.blit(textImg, (self.tile_size * 11.25, self.tile_size * 8.34))

    def drawPauseInfo(self, window):
        tile = self.tile_size
        if not self.GAME.gameOver and not self.GAME.paused:
            info = self.font.render('Press SPACE to pause', 1, 'White')
            window.blit(info, (self.tile_size * 10.6, self.tile_size * 6))

    def pop_up(self):
        tile = self.tile_size
        if self.GAME.gameOver:
            panel = pygame.Surface((tile * 4, tile * 5))
            message = "Black Won!!" if self.player1Score > self.player2Score \
                else "White Won!!" if self.player1Score < self.player2Score \
                else "Tie!!"
            end_text = self.font.render(message, 1, 'White')
            panel.blit(end_text, (tile / 2, tile / 2))

            if (self.GAME.is_recording or self.GAME.is_appending) and self.GAME.turn_count > 1:
                record_text = self.font.render('Game saved to game_records/', 1, 'White')
                panel.blit(record_text, (tile / 2, tile))

            game_text = self.font.render('Play Again', 1, 'Black')
            pygame.draw.rect(panel, 'White', (tile, tile * 2, tile * 2, tile))
            panel.blit(game_text, (tile * 1.5, tile * 2.375))

            pygame.draw.rect(panel, 'White', (tile, tile * 3.5, tile * 2, tile))
            settings_text = self.font.render('Settings', 1, 'Black')
            panel.blit(settings_text, (tile * 1.6, tile * 3.875))

            return panel

        if self.GAME.paused:
            panel = pygame.Surface((tile * 4, tile * 5))
            record_text = self.font.render('Game paused...', 1, 'White')
            panel.blit(record_text, (tile / 2, tile / 2))

            game_text = self.font.render('Continue', 1, 'Black')

            pygame.draw.rect(panel, 'White', (tile, tile * 2, tile * 2, tile))
            panel.blit(game_text, (tile * 1.5, tile * 2.375))

            pygame.draw.rect(panel, 'White', (tile, tile * 3.5, tile * 2, tile))
            if self.GAME.mode == 0:
                settings_text = self.font.render('Quit', 1, 'Black')
                panel.blit(settings_text, (tile * 1.75, tile * 3.875))
            else:
                settings_text = self.font.render('Settings', 1, 'Black')
                panel.blit(settings_text, (tile * 1.6, tile * 3.875))

            return panel

    def drawGrid(self, window):
        tile = self.tile_size
        window.blit(self.gridBg, (0, 0))

        if self.GAME.is_recording:
            textImg = self.font.render('Recording', 1, 'Red')
            window.blit(textImg, (tile * 0.2, tile * 0.2))

        window.blit(self.drawScore('Black', self.player1Score), (tile * 11.2, tile))
        window.blit(self.drawScore('White', self.player2Score), (tile * 11.2, tile * 2))

        for token in self.tokens.values():
            token.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == self.GAME.human_player:
            for move in availMoves:
                pygame.draw.rect(window, 'White',
                                 (tile + (move[1] * tile) + tile * (3 / 8), tile + (move[0] * tile) + tile * (3 / 8),
                                  tile / 4, tile / 4))

        if self.GAME.gameOver or self.GAME.paused:
            window.blit(self.pop_up(), (tile * 3, tile * 2.5))

    def markRecentMove(self, window):
        tile = self.tile_size
        move = self.GAME.recent_move
        if move is not None:
            pygame.draw.rect(window, 'Red',
                             (tile + (move[1] * tile) + tile * 0.375, tile + (move[0] * tile) + tile * 0.375,
                              tile * 0.25, tile * 0.25))

    def markNextMove(self, window):
        tile = self.tile_size
        if self.GAME.mode == 0 and not self.GAME.gameOver:
            turn = self.GAME.turn_count
            if turn < self.GAME.data['turn_count']:
                move = self.GAME.data[f'recent_move{turn + 1}']
                # move_maker = self.GAME.data[f'recent_move{turn}'][2]
                # token_image = self.blacktoken.convert_alpha() if move[2] == 1 else self.whitetoken.convert_alpha()
                # token_image.set_alpha(144)
                # window.blit(token_image, (tile + move[1] * tile, tile + move[0] * tile))
                pygame.draw.rect(window, 'Green',
                                 (tile + (move[1] * tile) + tile * 0.425, tile + (move[0] * tile) + tile * 0.425,
                                  tile * 0.15, tile * 0.15))

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
        if len(surroundCells) == 0 or player is None:
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
