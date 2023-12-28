import copy
import random

# Computer player, implemented with searching algorithms and heuristics
# EDIT USED HEURISTICS / EVALUATING FUNCTIONS IN heuristics.py ONLY


class ComputerPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject

    def computerRandom(self, grid, player):
        availMoves = self.grid.findAvailMoves(self.grid.gridLogic, player)
        return random.choice(availMoves), 0

    def computerMABP(self, grid, heuristics, depth, alpha, beta, player, turn_count):
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, heuristics(grid, turn_count)
            return bestMove, Score

        if player > 0:
            bestScore = alpha
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerMABP(newGrid, heuristics, depth - 1, alpha, beta, player * -1, turn_count + 1)

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore

        if player < 0:
            bestScore = beta
            bestMove = availMoves[0]

            for move in availMoves:
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles:
                    newGrid[tile[0]][tile[1]] = player

                bMove, value = self.computerMABP(newGrid, heuristics, depth - 1, alpha, beta, player * -1, turn_count + 1)

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid)
            return bestMove, bestScore
