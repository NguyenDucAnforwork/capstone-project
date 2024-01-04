from utility_functions import *
import time
from copy import deepcopy

GAMES, COUNT, MOVES, PROBA, FULL_EDGE = [], {}, {}, {}, {}   # proba[edge][move]

def potentialMove(grid, edge, player):
    validMove, sth = find_avail_moves_global(grid, player)
    Move, legalMove, possibleMove = [], [], []
    archor = edge[-1]
    if archor == (0,-100):
        X_square = [(1,1), (1,6)]
    if archor == (-100,7):
        X_square = [(1,6), (6,6)]
    if archor == (7,-100):
        X_square = [(6,6), (6,1)]
    if archor == (-100,0):
        X_square = [(6,1), (1,1)]

    # we only care about move at each edge
    for square in X_square:
        if square in validMove:
            Move.append(square)

    archor = edge[-1]
    for index in range(len(edge[:-3])):
        if archor[0] >= 0 and (archor[0], index) in validMove:
            Move.append((archor[0], index))
        if archor[1] >= 0 and (index, archor[1]) in validMove:
            Move.append((index, archor[1]))

    # legal move/possible move
    for move in Move:
        check = False
        swappable_tiles = swappable_tiles_global(move[0], move[1], grid, player)

        for tile in swappable_tiles:
            if tile[0] * (tile[0]-7) == 0 or tile[1] * (tile[1] - 7) == 0:
                check = True
                legalMove.append(move)
                break
            if tile in X_square:
                check = True
                legalMove.append(move)
                break
        # possible move
        if not check:
            possibleMove.append(move)
    
    return Move, legalMove, possibleMove

def convertTextToMove(game):
    moves = []
    N = len(game)
    for i in range(int((N + 1) / 2)):
        move = game[(2 * i):(2 * i + 2)]
        move1 = ord(move[0]) - ord('a')
        move2 = int(move[1]) - 1
        moves.append((move2, move1))
    return moves

def library(datapath):
    with open(datapath, "r") as file:
        for textGame in file:
            game = convertTextToMove(textGame.strip())
            GAMES.append(game)

# keep track of: edge pos + avail move:
def processGame(check, game, position, numMove, maxMove,  player):
    global MOVES
    # stop condition:
    if numMove == maxMove:
        coin_parity = (-1) * sum([num for row in position for num in row])
        for full_edge in check:
            if full_edge not in FULL_EDGE:
                FULL_EDGE[full_edge] = [0,0]
            FULL_EDGE[full_edge][0] += coin_parity
            FULL_EDGE[full_edge][1] += 1
            
        return 
    CONST = 100
    move = game[numMove]

    if len(swappable_tiles_global(move[0], move[1], position, player)) == 0:
        processGame(check, game, position, numMove, maxMove,  player*(-1))
    # extract edge position:
    else:
        edge1 = position[0].copy()
        edge1.extend([position[1][1], position[1][6], (0, -CONST)])
        
        edge2 = [position[i][7] for i in range(8)]
        edge2.extend([position[1][6], position[6][6], (-CONST, 7)])

        edge3 = position[7].copy()
        edge3.extend([position[6][6], position[6][1], (7, -CONST)])

        edge4 = [position[i][0] for i in range(8)]
        edge4.extend([position[6][1], position[1][1], (-CONST, 0)])

        # update edges + possible move of this current pos
        edges = [tuple(edge1), tuple(edge2), tuple(edge3), tuple(edge4)]
        tuple_pos = tuple(map(tuple, position))  # Convert position to tuple of tuples    for edge in edges:

        for edge in edges:
            full_edge = tuple((list(edge))[:-1])
            if sum(abs(num) for num in full_edge) == 10:
                if tuple(full_edge) not in check:
                    check[full_edge] = True

            Move, legalMove, possibleMove = potentialMove(position, edge, player)
            if len(legalMove) + len(possibleMove) > 0:
                if edge not in COUNT:
                    COUNT[edge] = {}
                    if tuple_pos not in COUNT[edge]:
                        COUNT[edge][tuple_pos] = 1
                else:
                    if tuple_pos not in COUNT[edge]:
                        COUNT[edge][tuple_pos] = 1
                    else:
                        COUNT[edge][tuple_pos] += 1

        # we only count it for the possible move
            if len(possibleMove) > 0:
                for move in possibleMove:
                    new_edge = (list(edge)).copy()
                    archor = new_edge[-1]
                    new_edge = tuple(new_edge[:-1])
                    new_move = (list(move)).copy()
                    if(archor[0] >= 0):
                        new_move[0] = 0
                        new_move[1] = move[1]
                    if archor[1] >= 0:
                        new_move[1] = move[0]
                        new_move[0] = 0
                    new_move = tuple(new_move)

                    if new_edge not in MOVES:
                        MOVES[new_edge] = {}
                    if new_move not in MOVES[new_edge]:
                        MOVES[new_edge][new_move] = 1
                    else:
                        MOVES[new_edge][new_move] += 1

        # update position
        move = game[numMove]    # dont know why this bug occurs
        if len(swappable_tiles_global(move[0], move[1], position, player)) == 0:
            return
        position[move[0]][move[1]] = player
        swappableTile = swappable_tiles_global(move[0], move[1], position, player)
        for tile in swappableTile:
            position[tile[0]][tile[1]] *= -1
        processGame(check, game, position, numMove+1, maxMove, player*(-1))

def gameProgress():
    initialPosition = (
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,-1,1,0,0,0],
        [0,0,0,1,-1,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    )
    library("database.txt")
    for game in GAMES:
        start = time.time()
        processGame({}, game, deepcopy(initialPosition), 0, len(game), 1)
        end = time.time()
        print(end-start)

gameProgress()

def printOut():
    # res = 0
    # for edge, value in COUNT.items():
    #     print(f"Edge: {edge}")
    #     for pos, count in value.items():
    #         res+= 1
    #         print(f"pos: {pos}, Count: {count}")
    # print(res)

    # res = 0
    # for edge, value in MOVES.items():
    #     print(f"Edge: {edge}")
    #     for move, count in value.items():
    #         res+= 1
    #         print(f"move: {move}, Count: {count}")
    # print(res)

    # for edge, value in MOVES.items():
    #     for move, count in value.items():
    #         PROBA[edge] = {}
    #         PROBA[edge][move] = {}
    #         a = sum([count for position, count in COUNT[edge].items()])
    #         PROBA[edge][move] = (MOVES[edge][move]) / a

    # count1, count2 = 0, 0

    # for edge, value in PROBA.items():
    #     for move, count in value.items():
    #         count1 += 1
    #         count2 += 1 if count == 1 else 0
    #         print(f"{edge}, {move}, {count}")
    # print(count2, count1)

    for edge, value in FULL_EDGE.items():
        print(f"edge: {edge}, value: {value}")

printOut()

def expectiminimax(edge):
    if sum([abs(move) for move in edge[:-1]]) == 10:
        # total disc parity / games that have that edge confi
        pass

