from utility_functions import *
import time
from copy import deepcopy
import json

GAMES, COUNT, MOVES, PROBA, FULL_EDGE, EVAL, CONST = [], {}, {}, {}, {}, {}, 100   # proba[edge][move]   # eval[edge_confi]
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

def extractEdge(position):
    edge1 = position[0].copy()
    edge1.extend([position[1][1], position[1][6], (0, -CONST)])
    
    edge2 = [position[i][7] for i in range(8)]
    edge2.extend([position[1][6], position[6][6], (-CONST, 7)])

    edge3 = position[7].copy()
    edge3.extend([position[6][1], position[6][6], (7, -CONST)])

    edge4 = [position[i][0] for i in range(8)]
    edge4.extend([position[1][1], position[1][6], (-CONST, 0)])
    return [tuple(edge1[:-1]), tuple(edge2[:-1]), tuple(edge3[:-1]), tuple(edge4[:-1])]

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
def processGame(check, game, position, numMove, maxMove,  player):
    MOVE_PLAYED, EDGE_BEFORE, EDGE_AFTER = ["No move" for _ in range(4)], [], []
    # stop condition:
    if numMove == maxMove:
        coin_parity = sum([num for row in position for num in row])
        for full_edge in check:
            if sum([abs(num) for num in full_edge]) == 10:
                if full_edge not in FULL_EDGE:
                    FULL_EDGE[full_edge] = [0,0]
                FULL_EDGE[full_edge][0] += coin_parity
                FULL_EDGE[full_edge][1] += 1
        return 
    move = game[numMove]
    # print(f"pos: {position}, Move: {numMove}, MaxMove: {maxMove}, player: {player}")
    if len(swappable_tiles_global(move[0], move[1], position, player)) == 0:
        processGame(check, game, position, numMove, maxMove,  player*(-1))
    
    else:
        legalMove = findLegalMoveInBoard(position, player)
        MOVE = game[numMove]    # dont know why this bug occurs
        edge1 = position[0].copy()
        edge1.extend([position[1][1], position[1][6], (0, -CONST)])
        
        edge2 = [position[i][7] for i in range(8)]
        edge2.extend([position[1][6], position[6][6], (-CONST, 7)])

        edge3 = position[7].copy()
        edge3.extend([position[6][1], position[6][6], (7, -CONST)])

        edge4 = [position[i][0] for i in range(8)]
        edge4.extend([position[1][1], position[1][6], (-CONST, 0)])

        # update edges + possible move of this current pos
        EDGE_BEFORE = extractEdge(position)
        tuple_pos = tuple(map(tuple, position))  # Convert position to tuple of tuples    for edge in edges:
        
        # convert move to its normalized position
        if MOVE not in legalMove:
            if MOVE[0] == 0:
                MOVE_PLAYED[0] = MOVE[1]
            if MOVE[0] == 7:
                MOVE_PLAYED[2] = MOVE[1]
            if MOVE[1] == 7:
                MOVE_PLAYED[1] = MOVE[0]
            if MOVE[1] == 0:
                MOVE_PLAYED[3] = MOVE[0]
            
            if MOVE == (1,1):
                MOVE_PLAYED[0], MOVE_PLAYED[3] = 8,8
            if MOVE == (1,6):
                MOVE_PLAYED[0], MOVE_PLAYED[1] = 9,8
            if MOVE == (6,6):
                MOVE_PLAYED[1], MOVE_PLAYED[2] = 9,9
            if MOVE == (6,1):
                MOVE_PLAYED[2], MOVE_PLAYED[3] = 8,9    
        # update position
        if len(swappable_tiles_global(MOVE[0], MOVE[1], position, player)) == 0:
            return
        position[MOVE[0]][MOVE[1]] = player
        swappableTile = swappable_tiles_global(MOVE[0], MOVE[1], position, player)
        for tile in swappableTile:
            position[tile[0]][tile[1]] *= -1
        EDGE_AFTER = extractEdge(position)
        COMBINE = [(edge_before, move, edge_after) for edge_before, move, edge_after in zip(EDGE_BEFORE, MOVE_PLAYED, EDGE_AFTER)]
        for edge_before, MOVE, edge_after in COMBINE:
            if edge_before not in MOVES:
                MOVES[edge_before] = {}
            if MOVE not in MOVES[edge_before]:
                MOVES[edge_before][MOVE] = {}
            if edge_after not in MOVES[edge_before][MOVE]:
                MOVES[edge_before][MOVE][edge_after] = 1
            else:
                MOVES[edge_before][MOVE][edge_after] += 1

        processGame(EDGE_AFTER, game, position, numMove+1, maxMove, player*(-1))

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
            if tuple(edge) in FULL_EDGE:
                EVAL[tuple(edge)] = FULL_EDGE[tuple(edge)][0] / FULL_EDGE[tuple(edge)][1]
                return FULL_EDGE[tuple(edge)][0] / FULL_EDGE[tuple(edge)][1]
            else:
               return 100
    possibleMove = []
    # find legal + possible move
    legalMove = findLegalMoveInEdge(edge, player)
    for index in range(len(edge)):
        if edge[index] == 0 and index not in legalMove:
            possibleMove.append(index)


    # max player
    if player == 1:
        newEdge = list(deepcopy(edge))
        bestScore = alpha
        # print(f"legal move: {legalMove} {edge} {player}")

        for move in legalMove:
            for tile in swappableTilesInEdge(move, newEdge, player):
                newEdge[tile] *= -1
            newEdge[move] = player
            # print(f"ủa là sao: {newEdge}, {move}")
            score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
            if score > bestScore:
                bestScore = score
            alpha = max(alpha, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)
        
        for move in possibleMove:
            res = 0
            # we need to make sure the position is not repeated. We treat this case as a legal move
            if move == "NO MOVE":
                if (player == 1 and blackPass == False):
                    score = expectiminimax(newEdge, player * (-1), True, whitePass, alpha, beta)
                    res += score
                    
            # chance node
            else:
                if tuple(newEdge) in MOVES:
                    if move in MOVES[tuple(newEdge)]:
                        totalScore = sum([MOVES[tuple(newEdge)][move][tuple(edge_after)] for edge_after in MOVES[tuple(newEdge)][move]])
                        # for edge_after in MOVES[tuple(newEdge)][move]:
                        edge_after = deepcopy(newEdge)
                        edge_after[move] = player
                        proba = MOVES[tuple(newEdge)][move][tuple(edge_after)] / totalScore if tuple(edge_after) in MOVES[tuple(newEdge)][move] else 1
                        # print(f"new edge: {newEdge} edge_after: {edge_after}   {player}")                            
                        score = expectiminimax(list(edge_after), player * -1, False, False, alpha, beta)
                        res += score * proba
                        # print(f"res: {res}")
                else:
                    # print(f"Nếu edge kh trong MOVES")
                    newEdge[move] = player
                    res = expectiminimax(list(newEdge), player * -1, False, False, alpha, beta)
                if res > bestScore:
                    bestScore = res
                    alpha = max(alpha, bestScore)
                    if beta <= alpha:
                        break
                newEdge = deepcopy(edge)

        EVAL[tuple(edge)] = bestScore    
        return bestScore
    

    if player == -1:
        newEdge = list(deepcopy(edge))
        bestScore = beta
        # print(f"legal move: {legalMove} {edge} {player}")

        for move in legalMove:
            for tile in swappableTilesInEdge(move, newEdge, player):   # pasing newEdge, not edge
                newEdge[tile] *= (-1)
            newEdge[move] = player

            score = expectiminimax(newEdge, player * (-1), False, False, alpha, beta)
            if score < bestScore:
                bestScore = score
            beta = min(beta, bestScore)
            if beta <= alpha:
                break
            newEdge = deepcopy(edge)

        for move in possibleMove:
            # we need to make sure the position is not repeated
            if move == "NO MOVE":
                if player == -1 and whitePass == False:
                    expectiminimax(edge, player * -1, blackPass, True, alpha, beta)
                    
            # chance node
            else:
                res = 0            
                if tuple(newEdge) in MOVES:
                    if move in MOVES[tuple(newEdge)]:
                        totalScore = sum([MOVES[tuple(newEdge)][move][tuple(edge_after)] for edge_after in MOVES[tuple(newEdge)][move]])
                        # for edge_after in MOVES[tuple(newEdge)][move]:
                        edge_after = deepcopy(newEdge)
                        edge_after[move] = player
                        proba = MOVES[tuple(newEdge)][move][tuple(edge_after)] / totalScore if tuple(edge_after) in MOVES[tuple(newEdge)][move] else 1
                        # print(f"new edge: {newEdge} edge_after: {edge_after}   {player}")
                        score = expectiminimax(list(edge_after), player * -1, False, False, alpha, beta)
                        res += score * proba
                        # print(f"res: {res}")

                else:
                    # print(f"Nếu edge kh trong MOVES")
                    newEdge[move] = player
                    res = expectiminimax(list(newEdge), player * -1, False, False, alpha, beta)
                if res < bestScore:
                    bestScore = res
                    beta = min(beta, bestScore)
                    if beta <= alpha:
                        break
                newEdge = deepcopy(edge)
        EVAL[tuple(edge)] = bestScore
        return bestScore

expectiminimax([0,0,0,0,0,0,0,0,0,0], 1, False, False, -100000,100000)

def saveResult():
    # for edge_before, moves1 in MOVES.items():
    #     for move, moves2 in moves1.items():
    #         for edge_after, count in moves2.items():
    #             print(f"Edge: {edge_before}, Move: {move}, Edge After: {edge_after}, Count: {count}")
    # for edge, value in FULL_EDGE.items():
    #     print(f"edge: {edge}, value: {value}")
    file_path = "full_edge_data.json"
    FULL_EDGE_str_keys = {str(key): value for key, value in FULL_EDGE.items()}

    # Ghi từ điển vào tập tin JSON
    # with open(file_path, 'w') as json_file:
    #     json.dump(FULL_EDGE_str_keys, json_file, indent=4)

saveResult()


# MOVES[edge][turn]