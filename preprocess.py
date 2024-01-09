from utility_functions import *
import time
from copy import deepcopy
import json

GAMES, COUNT, MOVES, PROBA, FULL_EDGE, EVAL, CONST = [], {}, {}, {}, {}, {}, 100   # proba[edge][move]   # eval[edge_confi]   #MOVES[edge][player][move]
X = [(1,1), (1,6), (6,1), (6,6)]

def swappableTilesInEdge(move, edge, player):
    DIRECTION = [1,-1]
    res = []
    for direction in DIRECTION:
        Move = move
        current = []
        while Move + direction < 8 and Move + direction >= 0 and edge[Move+direction] == player * (-1):
            current.append(Move+direction)
            Move += direction
        if Move >= 8 or Move < 0 or edge[Move+direction] != player:
            current.clear()
        else:
            if len(current) > 0:
                res.extend(current.copy())
    return res

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

def findLegalMoveInEdge(edge, player):
    res = []
    for index in range(len(edge)):
        if edge[index] == player:
            mark = index+1
            while mark < 8 and edge[mark] == player * (-1):
                mark += 1
            if mark  < 8 and mark >= 0 and mark != index+1 and edge[mark] == 0 and mark not in res:
                res.append(mark)
        if edge[index] == player:
            mark = index-1
            while mark < 8 and edge[mark] == player * (-1):
                mark -= 1
            if mark < 8 and mark >= 0 and mark != index-1 and edge[mark] == 0 and mark not in res:
                res.append(mark)
    return res
    
def findLegalMoveInBoard(position, player):
    availMoves = find_avail_moves_global(position, player)
    res = []
    for move in availMoves[0]:   # hard to understand this bug
        tiles = swappable_tiles_global(move[0], move[1], position, player)
        for tile in tiles:
            if tile[0] * (tile[0] - 7) == 0 or tile[1] * (tile[1] - 7) == 0:
                res.append(move)
                break
    return res

# keep track of: edge pos + avail move:
def processGame(EDGE, game, position, numMove, maxMove,  player):
    MOVE_PLAYED, EDGE_BEFORE, EDGE_AFTER = ["No move" for _ in range(4)], [], []
    # stop condition:
    if numMove == maxMove:
        coin_parity = sum([num for row in position for num in row])
        for full_edge in EDGE:
            # if sum([abs(num) for num in full_edge]) == 10:
                if full_edge not in FULL_EDGE:
                    FULL_EDGE[full_edge] = [0,0]
                FULL_EDGE[full_edge][0] += coin_parity
                FULL_EDGE[full_edge][1] += 1
        return 
    move = game[numMove]
    # print(f"pos: {position}, Move: {numMove}, MaxMove: {maxMove}, player: {player}")
    if len(swappable_tiles_global(move[0], move[1], position, player)) == 0:
        processGame(EDGE, game, position, numMove, maxMove,  player*(-1))
    
    else:
        legalMove = findLegalMoveInBoard(position, player)
        MOVE = game[numMove]    # dont know why this bug occurs

        # update edges + possible move of this current pos
        EDGE_BEFORE = extractEdge(position)
        tuple_pos = tuple(map(tuple, position))  # Convert position to tuple of tuples    for edge in edges:
        for edge in EDGE_BEFORE:
            if edge not in EDGE:
                EDGE.append(edge)
        # convert move to its normalized position
        # if MOVE not in legalMove:
        #     if MOVE[0] == 0:
        #         MOVE_PLAYED[0] = MOVE[1]
        #     if MOVE[0] == 7:
        #         MOVE_PLAYED[2] = MOVE[1]
        #     if MOVE[1] == 7:
        #         MOVE_PLAYED[1] = MOVE[0]
        #     if MOVE[1] == 0:
        #         MOVE_PLAYED[3] = MOVE[0]
            
        # if MOVE == (1,1):
        #     MOVE_PLAYED[0], MOVE_PLAYED[3] = 8,8
        # if MOVE == (1,6):
        #     MOVE_PLAYED[0], MOVE_PLAYED[1] = 9,8
        # if MOVE == (6,6):
        #     MOVE_PLAYED[1], MOVE_PLAYED[2] = 9,9
        # if MOVE == (6,1):
        #     MOVE_PLAYED[2], MOVE_PLAYED[3] = 8,9    
        # update position
        if len(swappable_tiles_global(MOVE[0], MOVE[1], position, player)) == 0:
            return
        position[MOVE[0]][MOVE[1]] = player
        swappableTile = swappable_tiles_global(MOVE[0], MOVE[1], position, player)
        for tile in swappableTile:
            position[tile[0]][tile[1]] *= -1
        # EDGE_AFTER = extractEdge(position)
        # COMBINE = [(edge_before, move) for edge_before, move in zip(EDGE_BEFORE, MOVE_PLAYED)]
        # for edge_before, move in COMBINE:
        #     if str(edge_before) not in MOVES:
        #         MOVES[str(edge_before)] = {}
        #     if str(player) not in MOVES[str(edge_before)]:
        #         MOVES[str(edge_before)][str(player)] = {}
        #     if str(move) not in MOVES[str(edge_before)][str(player)]:
        #         MOVES[str(edge_before)][str(player)][str(move)] = 1
        #     else:
        #         MOVES[str(edge_before)][str(player)][str(move)] += 1

        processGame(EDGE, game, position, numMove+1, maxMove, player*(-1))

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
        processGame([], game, deepcopy(initialPosition), 0, len(game), 1)
        end = time.time()
        print(end-start)

gameProgress()

def expectiminimax(edge, player, blackPass, whitePass, alpha, beta):
    if sum([abs(num) for num in edge]) == 10:
        bMove = None
        if tuple(edge) in FULL_EDGE:
            return bMove, FULL_EDGE[tuple(edge)][0] / FULL_EDGE[tuple(edge)][1]
        else:
            return bMove, 100
    newEdge = deepcopy(edge)
    # find legal + possible move
    possibleMove = ["NO MOVE"]
    legalMove = findLegalMoveInEdge(edge, player)
    for index in range(len(edge)):
        if edge[index] == 0 and index not in legalMove:
            possibleMove.append(index)
    # print(f"edge: {edge}, player: {player}, whitepass: {whitePass}, blackpass: {blackPass}, legal: {legalMove}, possible: {possibleMove}")

    # max player
    if player == 1:
        # if str(tuple(edge)) in EVAL:
        #     if str(player) in EVAL[str(tuple(edge))]:
        #         if str(move) in EVAL[str(tuple(edge))][str(player)]:
        #             return EVAL[str(tuple(edge))][str(player)][str(move)]
        bestScore = float('-inf')
        bestMove = None
        # print(f"legal move: {legalMove} {edge} {player}")

        for move in legalMove:
            for tile in swappableTilesInEdge(move, newEdge, player):
                newEdge[tile] *= -1
            print(f"{move}, {newEdge}")
            newEdge[move] = player
            # print(f"after that: {newEdge}")
            # print(f"ủa là sao: {newEdge}, {move}")
            bMove, score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
            # print(f"move: {bMove}, score: {score}")
            EVAL[tuple(edge)] = {}
            EVAL[tuple(edge)][str(player)] = {}
            EVAL[tuple(edge)][str(player)][str(move)] = score
            if score > bestScore:
                bestScore = score
                bestMove = move
            alpha = max(alpha, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)
        
        for move in possibleMove:
            # we need to make sure the position is not repeated. We treat this case as a legal move
            if move == "NO MOVE":
                if (player == 1 and blackPass == False):
                    bMove, score = expectiminimax(newEdge, player * (-1), True, whitePass, alpha, beta)
                    print(f"player {player}, edge {newEdge}, move: {bMove}, score: {score}")    
                    EVAL[str(tuple(edge))] = {}
                    EVAL[str(tuple(edge))][str(player)] = {}
                    EVAL[str(tuple(edge))][str(player)][str(move)] = score
                    if score > bestScore:
                        bestScore = score
                        bestMove = move
                    newEdge = deepcopy(edge)
            # chance node
            else:
                print(f"{move}, {newEdge}")
                newEdge[move] = player
                # print(f"after that: {newEdge}")
                bMove, score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
                # print(f"move: {bMove}, score: {score}")
                EVAL[str(tuple(edge))] = {}
                EVAL[str(tuple(edge))][str(player)] = {}
                EVAL[str(tuple(edge))][str(player)][str(move)] = score
                if score > bestScore:
                    bestScore = score
                    bestMove = move
            
            alpha = max(alpha, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)
        
        return bestMove, bestScore
    
        # max player
    if player == -1:
        # if str(tuple(edge)) in EVAL:
        #     if str(player) in EVAL[str(tuple(edge))]:
        #         if str(move) in EVAL[str(tuple(edge))][str(player)]:
        #             return EVAL[str(tuple(edge))][str(player)][str(move)]
        bestScore = float('inf')
        bestMove = None
        # print(f"legal move: {legalMove} {edge} {player}")

        for move in legalMove:
            for tile in swappableTilesInEdge(move, newEdge, player):
                newEdge[tile] *= -1
            newEdge[move] = player
            # print(f"ủa là sao: {newEdge}, {move}")
            bMove, score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
            EVAL[str(tuple(edge))] = {}
            EVAL[str(tuple(edge))][str(player)] = {}
            EVAL[str(tuple(edge))][str(player)][str(move)] = score
            if score < bestScore:
                bestScore = score
                bestMove = move
            beta = min(beta, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)
        
        for move in possibleMove:
            # we need to make sure the position is not repeated. We treat this case as a legal move
            if move == "NO MOVE":
                if (player == -1 and whitePass == False):
                    bMove, score = expectiminimax(newEdge, player * (-1), blackPass, True, alpha, beta)
                    print(f"player {player}, edge {newEdge}, move: {bMove}, score: {score}")                        
                    EVAL[str(tuple(edge))] = {}
                    EVAL[str(tuple(edge))][str(player)] = {}
                    EVAL[str(tuple(edge))][str(player)][str(move)] = score
                    if score < bestScore:
                        bestScore = score
                        bestMove = move
                    newEdge = deepcopy(edge)
            # chance node
            else:
                newEdge[move] = player
                bMove, score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
                EVAL[str(tuple(edge))] = {}
                EVAL[str(tuple(edge))][str(player)] = {}
                EVAL[str(tuple(edge))][str(player)][str(move)] = score
                if score < bestScore:
                    bestScore = score
                    bestMove = move
            beta = min(beta, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)
           
        return bestMove, bestScore

# expectiminimax([0,0,0,0,0,0,0,0,0,0], 1, False, False, -100000,100000)

def saveResult():
    file_path = "backup.json"
    EVAL_str_keys = {str(key): value for key, value in FULL_EDGE.items()}
    # Ghi từ điển vào tập tin JSON
    with open(file_path, 'w') as json_file:
        json.dump(EVAL_str_keys, json_file, indent=4)
saveResult()


# MOVES[edge][turn]