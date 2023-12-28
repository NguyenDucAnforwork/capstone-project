import pygame


# utility functions, needed for grid.py and heuristics.py
# important file, modifying this could break some (many) other functionalities

def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    """Check to determine which directions are valid from current cell"""
    valid_directions = []
    if x != minX: valid_directions.append((x-1, y))
    if x != minX and y != minY: valid_directions.append((x-1, y-1))
    if x != minX and y != maxY: valid_directions.append((x-1, y+1))

    if x!= maxX: valid_directions.append((x+1, y))
    if x != maxX and y != minY: valid_directions.append((x+1, y-1))
    if x != maxX and y != maxY: valid_directions.append((x+1, y+1))

    if y != minY: valid_directions.append((x, y-1))
    if y != maxY: valid_directions.append((x, y+1))

    return valid_directions


def loadImages(path, size):
    """Load an image into the game, and scale the image"""
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img


def loadSpriteSheet(sheet, row, col, newSize, size):
    """creates an empty surface, loads a portion of the spritesheet onto the surface, then return that surface as img"""
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image


# Global functions help assess grid
def find_valid_cells_global(grid, current_player):
    """Return a list of all empty cells that are adjacent to opposing player of current_player"""
    valid_cell_to_click = []
    for gridX, row in enumerate(grid):
        for gridY, col in enumerate(row):
            if grid[gridX][gridY] != 0:
                continue
            DIRECTIONS = directions(gridX, gridY)

            for direction in DIRECTIONS:
                dirX, dirY = direction
                checked_cell = grid[dirX][dirY]

                if checked_cell == 0 or checked_cell == current_player:
                    continue

                if (gridX, gridY) in valid_cell_to_click:
                    continue

                valid_cell_to_click.append((gridX, gridY))
    return valid_cell_to_click


def swappable_tiles_global(x, y, grid, current_player):
    """Return a list of all opponent's tiles being flipped if currentPlayer moves to (x, y)"""
    surround_cells = directions(x, y)
    if len(surround_cells) == 0:
        return []

    swappable_tiles = []
    for checkCell in surround_cells:
        checkX, checkY = checkCell
        difX, difY = checkX - x, checkY - y
        current_line = []

        RUN = True
        while RUN:
            if grid[checkX][checkY] == current_player * -1:
                current_line.append((checkX, checkY))
            elif grid[checkX][checkY] == current_player:
                RUN = False
                break
            elif grid[checkX][checkY] == 0:
                current_line.clear()
                RUN = False
            checkX += difX
            checkY += difY

            if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                current_line.clear()
                RUN = False

        if len(current_line) > 0:
            swappable_tiles.extend(current_line)

    return swappable_tiles


def find_avail_moves_global(grid, current_player):
    """Return a list of possible moves from currentPlayer"""
    valid_cells = find_valid_cells_global(grid, current_player)
    playable_cells = []
    unstable_cells = []

    for cell in valid_cells:
        x, y = cell
        if cell in playable_cells:
            continue
        swapTiles = swappable_tiles_global(x, y, grid, current_player)

        # if len(swapTiles) > 0 and cell not in playable_cells:
        if len(swapTiles) > 0:
            playable_cells.append(cell)

    return playable_cells, unstable_cells


def stable_disc(grid, player):
    """Return a list of stable discs of given player"""
    pairDirections = [[[0, 1], [0, -1]], [[-1, 0], [1, 0]], [[1, 1], [-1, -1]], [[-1, 1], [1, -1]]]
    discCoor = []
    for gridX, row in enumerate(grid):
        for gridY, col in enumerate(row):
            if grid[gridX][gridY] == player:
                discCoor.append([gridX, gridY])
    result = []
    for coor in discCoor:
        X, Y = coor[0], coor[1]
        check = True

        for pair in pairDirections:
            checkLeft = True
            checkRight = True
            left = pair[0]
            right = pair[1]
            leftX, leftY = left[0], left[1]
            rightX, rightY = right[0], right[1]
            while True:
                X, Y = X + leftX, Y + leftY
                if X * (X - 7) > 0 or Y * (Y - 7) > 0:
                    break
                if grid[X][Y] != player:
                    checkLeft = False
                    break
            X, Y = coor[0], coor[1]

            while True:
                X, Y = X + rightX, Y + rightY
                if X * (X - 7) > 0 or Y * (Y - 7) > 0:
                    break
                if grid[X][Y] != player:
                    checkRight = False
                    break

            if not checkLeft and not checkRight:
                check = False
        if check:
            result.append(coor)

    return result
