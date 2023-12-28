import pygame
from othello import Othello
from prompt import Prompt

if __name__ == '__main__':

    settings = Prompt()
    options = list(settings.run())

    while True:
        game = Othello(*options, screen_height=settings.height, random_sprite=settings.random_sprite)
        reselect, next_mode, game_file = game.run()

        if next_mode == 0:
            break
        if reselect == 1:
            settings.reselect()
            options = list(settings.run())
            continue
        elif reselect == 2:
            settings.restart()
            options = list(settings.run())
            continue

        options[0] = next_mode
        options[-1] = game_file

    pygame.quit()
