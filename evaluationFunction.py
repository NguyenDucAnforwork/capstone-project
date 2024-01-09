from utility_functions import *
import json

# Heuristics
# Functions must have 2 parameters: grid_object and turn_count
# if you want to protect a function from being selectable, add '_' before the name
# for example: _corner, _xSquare won't be selectable

with open("table.json", "r") as file:
    TABLE = json.load(file)

def coin_parity(grid, turn_count):
    # Direction 1: maximizing B/W disks ratio
    B = 0
    W = 0
    for y, row in enumerate(grid):
        for x, col in enumerate(row):
            if col == 1:
                B += 1
            elif col == -1:
                W += 1
    disk_ratio = 100 * (B / (B + W)) if B > W else -100 * (W / (B + W)) if B < W else 0

    # Direction 2: maximizing disks number advantage
    disk_count = sum([sum(row) for row in grid])

    return disk_count


def mobility(grid, turn_count):
    # actual/potential mobility: For simplicity I would use the most simple form
    moves = {1: [], -1: []}
    moves[1], swappable_white = find_avail_moves_global(grid, 1)
    moves[-1], swappable_black = find_avail_moves_global(grid, -1)

    # coefficients:
    corner = 10
    X = -5
    C = -3
    edge = 0.5

    # potential mobility: I would calculate the number of frontier/outside discs
    frontier = {1: [], -1: []}
    hole = {1: [], -1: []}
    for gridX, row in enumerate(grid):
        for gridY, col in enumerate(row):
            if grid[gridX][gridY] != 0:
                player = grid[gridX][gridY]
                valid_directions = []
                if gridX != 0: valid_directions.append((gridX - 1, gridY))
                if gridX != 7: valid_directions.append((gridX + 1, gridY))
                if gridY != 0: valid_directions.append((gridX, gridY - 1))
                if gridY != 7: valid_directions.append((gridX, gridY + 1))

                for direction in valid_directions:
                    if (grid[direction[0]][direction[1]] == 0 and (gridX, gridY) not in frontier[player]
                            and (direction[0], direction[1] not in moves[player * -1])):
                        frontier[player].append((gridX, gridY))
                        if (direction[0], direction[1]) not in hole[player]:
                            hole[player].append((direction[0], direction[1]))
                        break
    
    # weight of the corner/X + C squares/remaining edge squares
    corner_square = [(0, 0), (0, 7), (7, 7), (7, 0)]
    C_square = [(0, 1), (1, 0), (0, 6), (7, 1), (6, 0), (7, 1), (7, 6), (6, 7)]
    X_square = [(1, 1), (6, 6), (6, 1), (6, 6)]
    edge_square = [(0, 2), (0, 3), (0, 4), (0, 5), (7, 4), (7, 5), (7, 2), (7, 3), (2, 0), (3, 0), (4, 0), (5, 0),
                   (2, 7), (3, 7), (4, 7), (5, 7)]

    # calculate the total mobility
    black_mobility = 2 / 5 * len(moves[1]) + 3 / 5 *( len(frontier[-1]) + len(hole[-1])) if len(moves[-1]) > 0 else -1000
    white_mobility = 2 / 5 * len(moves[-1]) + 3 / 5 *( len(frontier[1]) + len(hole[1])) if len(moves[-1]) > 0 else -1000


    # take into account the quality of the move
    for square in corner_square:
        if grid[square[0]][square[1]] == 1:
            black_mobility += corner
        if grid[square[0]][square[1]] == -1:
            white_mobility += corner

    for square in X_square:
        if grid[square[0]][square[1]] == 1:
            black_mobility += X
        if grid[square[0]][square[1]] == -1:
            white_mobility += X

    # configuration of 2 main diagonals
    config1 = (1 - grid[1][1] ** 2) * (1 - grid[6][6] ** 2) * grid[2][2] * grid[3][3] * grid[4][4] * grid[5][5] * grid[2][2]
    config2 = (1 - grid[6][1] ** 2) * (1 - grid[1][6] ** 2) * grid[2][5] * grid[3][4] * grid[4][3] * grid[5][2] * grid[2][5]
    config3 = (1 - grid[1][1] ** 2) * (1 - grid[6][6] ** 2) * grid[2][2] * grid[5][5] * grid[2][2]
    config4 = (1 - grid[6][1] ** 2) * (1 - grid[1][6] ** 2) * grid[2][5] * grid[5][2] * grid[2][5]

    res = black_mobility - white_mobility 
    if moves[1] == 0 or moves[1] == 1:
        res -= 1000000
    if moves[-1] == 0 or moves[-1] == 1:
        res += 1000000
    return res


def stability1(grid, turn_count):
    # unstable: each disc = -1
    black_move, white_unstable = find_avail_moves_global(grid, 1)
    white_move, black_unstable = find_avail_moves_global(grid, -1)

    # semi-stable: each disc = 0
    weight1 = (1-grid[0][1] ** 2)*(1- grid[0][6] ** 2)*grid[0][2]*grid[0][5] * grid[0][2] * grid[0][1] * grid[0][7]
    weight2 = (1 - grid[7][1] ** 2) * (1 - grid[7][6] ** 2) * grid[7][2] * grid[7][5] * grid[7][2] * grid[7][1] * grid[7][6]
    weight3 = (1 - grid[1][0]**2)*(1 - grid[6][0] ** 2)*grid[5][0] * grid[2][0] * grid[2][0] * grid[1][0] * grid[6][0]
    weight4 = (1 - grid[1][7] ** 2) * (1 - grid[6][7] ** 2) * grid[2][7] * grid[5][7] * grid[2][7] * grid[1][7] * grid[6][7]
    # stable: each disc = 1
    
    black_stable = stable_disc(grid, 1)
    white_stable = stable_disc(grid, -1)
    return 100*(weight1+weight2+weight3+weight4) + len(black_move) - len(white_move) - len(white_unstable) + len(black_unstable)

def combination(grid, count):
    edges = extractEdge(grid)
    res = 0
    for edge in edges:
        if str(edge) in TABLE:
            res += 100*TABLE[str(edge)]
    if count < 20:
        result = mobility(grid, count)
        
    else:
        result = res
    return result 

def _xSquare(grid, turn_count):
    coordinates = (
        [1, 1], [6, 6],
        [6, 1], [1, 6],
    )

    black_disks = sum([1 if grid[coor[0]][coor[1]] == 1 else 0 for coor in coordinates])
    white_disks = sum([1 if grid[coor[0]][coor[1]] == -1 else 0 for coor in coordinates])

    return -5 * black_disks + 5 * white_disks


def _corner(grid, turn_count):
    coordinates = (
        [0, 0], [0, 7],
        [7, 0], [7, 7],
    )

    black_disks = sum([1 if grid[coor[0]][coor[1]] == 1 else 0 for coor in coordinates])
    white_disks = sum([1 if grid[coor[0]][coor[1]] == -1 else 0 for coor in coordinates])

    return 10 * black_disks - 10 * white_disks


def _corner_occupancy(grid, turn_count):
    corner = [[0, 0], [0, 7], [7, 0], [7, 7]]
    white_corner = sum([1 if grid[cor[0]][cor[1]] == 1 else 0 for cor in corner])
    black_corner = sum([1 if grid[cor[0]][cor[1]] == -1 else 0 for cor in corner])
    return 25 * white_corner - 25 * black_corner


# need to build dynamic weight
def dynamic_weight(grid, turn_count):
    weight1 = [[6,-3,2,3,3,2,-3,6],
                [-3,-4,-1,-1,-1,-1,-4,-3],
                [2,-1,1,3,3,1,-1,2],
                [3,-1,3,5,5,3,-1,2],
                [3,-1,3,5,5,3,-1,2],
                [2,-1,1,3,3,1,-1,2],
                [-3,-4,-1,-1,-1,-1,-4,-3],
                [6,-3,2,3,3,2,-3,6],
                ]
    weight2 = [
        [120, -20, 40, 5, 5, 40, -20, 120],
        [-20, -80, -5, -5, -5, -5, -80, -20],
        [40, -5, 25, 3, 3, 25, -5, 40],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [5, -5, 3, 3, 3, 3, -5, 5],
        [40, -5, 25, 3, 3, 25, -5, 40],
        [-20, -80, -5, -5, -5, -5, -80, -20],
        [120, -20, 40, 5, 5, 40, -20, 120],
    ]

    if turn_count < 22:
        res = (sum([int(grid[i][j]) * int(weight1[i][j]) for i in range(0, 8) for j in range(0, 8)])) 
    else:
        res = (sum([int(grid[i][j]) * int(weight2[i][j]) for i in range(0, 8) for j in range(0, 8)])) 
    return res 


def _static_weight_ending(grid, turn_count):
    weight = [
        [120, -20, 20, 5, 5, 20, -20, 120],
        [-20, -40, 0, 0, 0, 0, -40, -20],
        [20, 0, 0, 0, 0, 0, 0, 20],
        [5, 0, 0, 0, 0, 0, 0, 5],
        [5, 0, 0, 0, 0, 0, 0, 5],
        [20, 0, 0, 0, 0, 0, 0, 20],
        [-20, -40, 0, 0, 0, 0, -40, -20],
        [120, -20, 20, 5, 5, 20, -20, 120],
    ]
    res = sum([int(grid[i][j]) * int(weight[i][j]) for i in range(0, 8) for j in range(0, 8)])
    return res / 20


def iago(grid, turn_count):
    white_stable = stable_disc(grid, -1)
    edge_stability = 0
    internal_stability = 0

    for disks in stable_disc(grid, 1):
        y, x = disks[0], disks[1]
        if y in (0, 7) and x in (0, 7):
            edge_stability += 70
        elif y == 0 or y == 7 or x == 0 or x == 7:
            edge_stability += 100
        else:
            internal_stability += 1

def stability3(grid, count):
    # unstable
    blackMoves, unstableWhiteTiles = find_avail_moves_global(grid, 1)
    whiteMoves, unstableBlackTiles = find_avail_moves_global(grid, -1)

    # stable
    whiteStable = stable_disc(grid, -1)
    blackStable = stable_disc(grid, 1)

    res = 0.4*(len(blackMoves) - len(whiteMoves)) + 0.6 * (len(unstableWhiteTiles) - len(unstableBlackTiles)) 

    # eval edge pos

    return res

def stability2(grid, count):
    edges = extractEdge(grid)
    res = 0
    for edge in edges:
        if str(edge) in TABLE:
            res += 100*TABLE[str(edge)]

    return res

def stability(grid, count):
    numW = 0
    numB = 0 
    A_square = [[0,2],[0,5],[2,0],[2,7],[5,0],[5,7],[7,2],[7,5]]
    B_square = [[3,0],[4,0],[0,3],[0,4],[3,7],[4,7],[7,3],[7,4]]
    C_square = [[0,1],[0,6],[1,0],[1,7],[6,0],[6,7],[7,1],[7,6]]
    X_square = [[1,1],[1,6],[6,1],[6,6]]
    corrner = [[0,0],[0,7],[7,0],[7,7]]
    # unstable
    whiteMoves, unstableBlackTiles = find_avail_moves_global(grid, -1)
    blackMoves, unstableWhiteTiles = find_avail_moves_global(grid, 1)
    if len(unstableWhiteTiles) !=0:
        for i in range(len(unstableWhiteTiles[0])):
            if list(unstableWhiteTiles[0][i]) in A_square:
                numW +=20
            if list(unstableWhiteTiles[0][i]) in B_square:
                numW +=15
            if list(unstableWhiteTiles[0][i]) in C_square:
                numW-=50
            if list(unstableWhiteTiles[0][i]) in X_square:
                numW-=75
    if len(unstableBlackTiles) !=0:
        for i in range(len(unstableBlackTiles[0])):
            if list(unstableBlackTiles[0][i]) in A_square:
                numB +=20
            if list(unstableBlackTiles[0][i]) in B_square:
                numB +=15
            if list(unstableBlackTiles[0][i]) in C_square:
                numB-=50
            if list(unstableBlackTiles[0][i]) in X_square:
                numB-=75          
    
    
    # stable
    whiteStable = stable_disc(grid, -1)
    blackStable = stable_disc(grid, 1)
    
    if len(whiteStable) !=0:
        for i in range(len(whiteStable)):
            if whiteStable[i] in A_square:
                numW +=1000
            if whiteStable[i] in B_square:
                numW +=1000
            if whiteStable[i] in C_square:
                numW +=1200
            if whiteStable[i] in X_square:
                numW +=1500
            if whiteStable[i] in corrner:
                numW +=8000
            else:
                numW +=10
    if len(blackStable) !=0:
        for i in range(len(blackStable)):
            if blackStable[i] in A_square:
                numB +=1000
            if blackStable[i] in B_square:
                numB +=1000
            if blackStable[i] in C_square:
                numB +=1200
            if blackStable[i] in corrner:
                numB +=8000
            if blackStable[i] in X_square:
                numB +=1500
            else:
                numB +=10
    

    # semi-stable
    semistablewhite=[]
    if len(unstableWhiteTiles)!=0:
        for i in range(len(unstableWhiteTiles[0])):
            if list(unstableWhiteTiles[0][i]) not in whiteStable:
                semistablewhite.append(unstableWhiteTiles[0][i])
    if len(semistablewhite)!=0:
        for i in range(len(semistablewhite)):
            if list(semistablewhite[i]) in A_square:
                numW +=100
            if list(semistablewhite[i]) in B_square:
                numW+=100
            if list(semistablewhite[i]) in C_square:
                numW -=125
            if list(semistablewhite[i]) in X_square:
                numW -=200
            else:
                numW +=5
    semistableblack=[]
    if len(unstableBlackTiles)!=0:
        for i in range(len(unstableBlackTiles[0])):
            if list(unstableBlackTiles[0][i]) not in blackStable:
                semistableblack.append(unstableBlackTiles[0][i])
    if len(semistableblack)!=0:
        for i in range(len(semistableblack)):
            if list(semistableblack[i]) in A_square:
                numB +=100
            if list(semistableblack[i]) in B_square:
                numB+=100
            if list(semistableblack[i]) in C_square:
                numB -=125
            if list(semistableblack[i]) in X_square:
                numB -=200
            else:
                numB +=5
    #return len(whiteStable) - len(blackStable)
    return (numB - numW)//100