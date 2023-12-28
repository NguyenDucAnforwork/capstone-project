import pygame
import copy
import time
import importlib
from grid import Grid
from computer import ComputerPlayer
from heuristics import *


# Othello: main game object, responsible for assigning turns and updating board


class Othello:
    def __init__(self, mode: int = 0, is_recording: bool = False, imported_file_path: str = None):
        """
        :param mode: 0: replay | 1: human vs. AI | 2: AI vs. AI | 3: AI vs. engine
        :param is_recording: whether the current game is being recorded
        :param imported_file_path: relative path to game record for replay
        """
        pygame.init()
        self.mode = mode
        self.is_recording = is_recording
        self.is_appending = False
        self.imported_f_path = imported_file_path

        # ADVANCED SETTINGS #
        base_height = 600  # window height, MUST be multiple of 10
        self.random_sprite = False  # turn on if you want some fun
        #####################

        # METRICS/CONDITIONS #
        self.time = 0
        self.turn_count = 0 if self.mode == 0 else 1
        self.gameOver = True
        self.forfeited_turns = 0
        self.player1 = 1  # black player
        self.player2 = -1  # white player
        self.currentPlayer = self.player1  # black always goes first
        ######################

        # CORE OBJECTS INITIALIZATION #
        self.tile_size = base_height // 10
        self.screen = pygame.display.set_mode((base_height * (4 / 3), base_height))
        self.grid = Grid(8, 8, (self.tile_size, self.tile_size), self)
        self.computerPlayer = ComputerPlayer(self.grid)
        ###############################

        # ROLLBACK #
        self.states = list()
        self.recent_move = None
        ############

        # GAME REPLAYING #
        if self.mode <= 0:
            pkg, self.imported_f_name = self.imported_f_path.split('/')
            mod = importlib.import_module(f'.{self.imported_f_name[:-3:]}', package=pkg)
            self.data = mod.data
            self.is_recording = False
            self.is_appending = False
        ##################

        # GAME RECORDING #
        if self.mode and self.is_recording:
            t = time.localtime()
            self.exported_f_path = (f'game_records/Game_{t.tm_mday:0>2d}{t.tm_mon:0>2d}{str(t.tm_year % 100).zfill(2)}'
                                    f'_{t.tm_hour:0>2d}{t.tm_min:0>2d}{t.tm_sec:0>2d}.py')
            self.is_written = False
        ##################

        # GAME RECONSTRUCTING #
        if self.mode < 0:
            true_turn = self.data['turn_count']
            self.gameOver = False
            for turn in range(true_turn):
                board = self.data[f'board{turn}']
                if turn == 0:
                    recent_move = None
                elif turn == 1:
                    recent_move = (self.data[f'recent_move{turn}'][0], self.data[f'recent_move{turn}'][1],
                                   self.data[f'recent_move{turn}'][2] * -1)
                else:
                    recent_move = (self.data[f'recent_move{turn}'][0], self.data[f'recent_move{turn}'][1],
                                   self.data[f'recent_move{turn - 1}'][2])
                self.states.append((board, recent_move))
            self.grid.recoverGrid(self.data[f'board{true_turn}'])
            self.recent_move = (self.data[f'recent_move{true_turn}'][0], self.data[f'recent_move{true_turn}'][1],
                                self.data[f'recent_move{true_turn - 1}'][2])
            self.turn_count = true_turn + 1
            self.exported_f_path = self.imported_f_path
            self.mode = -self.mode
            self.is_appending = True
            self.is_written = False
        #######################

        # WINDOW CAPTION #
        # caption = (f'Othello'
                #    f'{f' - Replaying /{self.imported_f_path}' if self.mode == 0 else ''}'
                #    f'{f' - Recording to /{self.exported_f_path}' if self.is_recording else ''}'
                #    f'{f' - Appending to /{self.exported_f_path}' if self.is_appending else ''}'
                #    f'{f' - Human vs. AI' if abs(self.mode) == 1 else ' - AI vs. Human' if abs(self.mode) == 3 else ''}'
                #    f'{' - AI vs. AI' if self.mode == 2 else ''}'
                #    f'{' - I\'m feeling lucky' if self.random_sprite else ''}')
        caption = 'lmao'
        pygame.display.set_caption(caption)
        ##################

        # GAME RULE #
        if self.mode == 1:
            self.human_player, self.AI_black, self.AI_white = (1, 0, -1)
        elif self.mode == 2:
            self.human_player, self.AI_black, self.AI_white = (0, 1, -1)
        elif self.mode == 3:
            self.human_player, self.AI_black, self.AI_white = (-1, 0, 1)
        elif self.mode == 0:
            if self.data['game_mode'] == 1:
                self.human_player, self.AI_black, self.AI_white = (1, 0, 0)
            elif self.data['game_mode'] == 2:
                self.human_player, self.AI_black, self.AI_white = (0, 0, 0)
            elif self.data['game_mode'] == 3:
                self.human_player, self.AI_black, self.AI_white = (-1, 0, 0)
        #############

        self.RUN = True
        self.NEXT_MODE = 0
        self.APPEND_FILE_PATH = None

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()
        return self.NEXT_MODE, self.APPEND_FILE_PATH

    def input(self):
        tile = self.tile_size
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            # General event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.grid.printGameLogicBoard()
                if event.button == 1:
                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 4 and x <= tile * 6 and y >= tile * 5 and y <= tile * 6:
                            if self.is_appending:
                                self.NEXT_MODE = self.mode
                                self.RUN = False
                            self.grid.newGame(self.random_sprite)
                            self.gameOver = False
                            self.currentPlayer = self.player1
                            self.recent_move = None
                            self.states = list()
                            self.turn_count = 0 if self.mode == 0 else 1

            # Human player move/rollback
            if event.type == pygame.MOUSEBUTTONDOWN and self.mode != 0:
                if event.button == 1:
                    # Move
                    if self.currentPlayer == self.human_player and not self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - tile) // tile, (y - tile) // tile
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if not validCells:
                            pass
                        else:
                            if (y, x) in validCells:
                                self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                                self.recent_move = (y, x, self.currentPlayer)
                                self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, y, x)
                                swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                                for tile in swappableTiles:
                                    self.grid.animateTransitions(tile, self.currentPlayer)
                                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                self.turn_count += 1
                                self.currentPlayer *= -1
                                self.forfeited_turns = 0
                                self.time = pygame.time.get_ticks()
                    # Rollback
                    if self.currentPlayer == self.human_player and not self.gameOver and self.turn_count >= 3:
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 10.8 and x <= tile * 12.4 and y >= tile * 8 and y <= tile * 9:
                            if self.states.pop():
                                self.turn_count -= 1
                            prev_board, prev_recent_move = self.states.pop()
                            self.grid.recoverGrid(prev_board)
                            self.recent_move = prev_recent_move
                            self.turn_count -= 1
                            return

            # Replay control
            if self.mode == 0:
                # Replay roll backward/forward
                if event.type == pygame.KEYDOWN and not self.gameOver:
                    if event.key == pygame.K_LEFT:
                        if self.turn_count > 0:
                            self.turn_count -= 1
                        elif self.turn_count == 0:
                            self.turn_count = self.data['turn_count']
                        self.grid.recoverGrid(self.data[f'board{self.turn_count}'])
                        self.recent_move = self.data[f'recent_move{self.turn_count}']
                        if self.recent_move is None:
                            self.currentPlayer = self.player1
                        else:
                            self.currentPlayer = self.data[f'recent_move{self.turn_count}'][2]
                    if event.key == pygame.K_RIGHT:
                        if self.turn_count < self.data['turn_count']:
                            self.turn_count += 1
                        elif self.turn_count == self.data['turn_count']:
                            self.turn_count = 0
                        self.grid.recoverGrid(self.data[f'board{self.turn_count}'])
                        self.recent_move = self.data[f'recent_move{self.turn_count}']
                        if self.recent_move is None:
                            self.currentPlayer = self.player1
                        else:
                            self.currentPlayer = self.data[f'recent_move{self.turn_count}'][2]
                # Branch into new game record
                if event.type == pygame.MOUSEBUTTONDOWN and not self.gameOver:
                    if event.button == 1 and self.mode == 0 and self.currentPlayer == self.human_player:
                        x, y = pygame.mouse.get_pos()
                        if x >= tile * 10.8 and x <= tile * 12.4 and y >= tile * 8 and y <= tile * 9:
                            self.NEXT_MODE = -self.data['game_mode']
                            t = time.localtime()
                            self.APPEND_FILE_PATH = (f'game_records/{self.imported_f_name[:-3:]}'
                                                     f'_{t.tm_mday:0>2d}{t.tm_mon:0>2d}{str(t.tm_year % 100).zfill(2)}'
                                                     f'_{t.tm_hour:0>2d}{t.tm_min:0>2d}{t.tm_sec:0>2d}'
                                                     f'_b{self.turn_count}.py')
                            f = open(self.APPEND_FILE_PATH, 'w')
                            f.write('data = {\n')
                            f.write(f'\t"game_mode": {self.data["game_mode"]},\n')
                            f.write(f'\t"turn_count": {self.turn_count},\n')
                            for turn in range(self.turn_count + 1):
                                f.write(f'\t"board{turn}": {str(self.data[f"board{turn}"])},\n')
                                f.write(f'\t"recent_move{turn}": {str(self.data[f"recent_move{turn}"])},\n')
                            f.write('}')
                            f.close()
                            self.RUN = False

    def update(self):
        # AI_white's turn
        if self.currentPlayer == self.AI_white and not self.gameOver:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                        self.gameOver = True
                        return
                    self.states.append(None)
                    self.currentPlayer *= -1
                if self.currentPlayer == self.AI_white:

                    cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 3, -100, 100,
                                                                   self.AI_white)
                    # cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.player_AI_min)

                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.recent_move = (cell[0], cell[1], self.currentPlayer)
                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.turn_count += 1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        # AI_black's turn
        if self.currentPlayer == self.AI_black and not self.gameOver:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100:
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.forfeited_turns += 1
                    if self.forfeited_turns == 2:
                        self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                        self.gameOver = True
                        return
                    self.states.append(None)
                    self.currentPlayer *= -1
                if self.currentPlayer == self.AI_black:

                    # cell, score = self.computerPlayer.computerHard(self.grid.gridLogic, coinParity, 3, -100, 100, self.player_AI_max)
                    cell, score = self.computerPlayer.computerRandom(self.grid.gridLogic, self.AI_black)

                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.recent_move = (cell[0], cell[1], self.currentPlayer)
                    self.grid.insertToken(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1])
                    swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                    for tile in swappableTiles:
                        self.grid.animateTransitions(tile, self.currentPlayer)
                        self.grid.gridLogic[tile[0]][tile[1]] *= -1
                    self.turn_count += 1
                    self.currentPlayer *= -1
                    self.forfeited_turns = 0

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)

        # human_player's turn
        if self.currentPlayer == self.human_player and not self.gameOver:
            if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                self.forfeited_turns += 1
                if self.forfeited_turns == 2:
                    self.states.append((copy.deepcopy(self.grid.gridLogic), self.recent_move))
                    self.gameOver = True
                    return
                self.states.append(None)
                self.currentPlayer *= -1

        if self.is_recording or self.is_appending:
            if self.gameOver and self.turn_count > 1 and not self.is_written:
                self.states = list(filter(lambda s: s is not None, self.states))
                f = open(self.exported_f_path, 'w')
                f.write('data = {\n')
                f.write(f'\t"game_mode": {self.mode},\n')
                f.write(f'\t"turn_count": {self.turn_count - 1},\n')
                for turn in range(self.turn_count):
                    board, recent_move = self.states[turn]
                    next_mover = self.states[turn + 1][1][2] if turn < self.turn_count - 1 else None
                    f.write(f'\t"board{turn}": {str(board)},\n')
                    if recent_move is None:
                        f.write(f'\t"recent_move{turn}": {str(recent_move)},\n')
                        continue
                    f.write(f'\t"recent_move{turn}": ({recent_move[0]}, {recent_move[1]}, {next_mover}),\n')
                f.write('}')
                self.is_written = True
                f.close()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        self.grid.markRecentMove(self.screen)
        self.grid.markNextMove(self.screen)
        self.grid.drawTurns(self.screen)
        self.grid.drawRollbackButton(self.screen)
        self.grid.drawBranchButton(self.screen)
        pygame.display.update()
