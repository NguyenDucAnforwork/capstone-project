import pygame
import pygame_menu as pm
import os
import heuristics
from inspect import getmembers, isfunction

# Settings Prompts


class Prompt:
    def __init__(self, base=600):
        pygame.init()

        HEIGHT = base
        WIDTH = base * (4 / 3)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Othello - Settings')

        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        CYAN = (0, 100, 100)
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        theme = pm.themes.THEME_DARK.copy()
        image = pm.baseimage.BaseImage(image_path='assets/cool.jpg', drawing_mode=pm.baseimage.IMAGE_MODE_FILL)
        image.apply_image_function(image_function=lambda r, g, b, a: (r * 0.3, g * 0.3, b * 0.3, a))
        theme.background_color = image
        theme.title_background_color = (255, 255, 255, 0)
        theme.widget_font_size = int(base * 0.04)

        # Prompts initialization
        self.main_menu = pm.Menu(title="Othello AI", height=HEIGHT, width=WIDTH, theme=theme)
        self.game_settings = pm.Menu(title="Game Settings", height=HEIGHT, width=WIDTH, theme=theme)
        self.func_settings = pm.Menu(title="Evaluating Functions", height=HEIGHT, width=WIDTH, theme=theme)
        self.replay_settings = pm.Menu(title="Replay Settings", height=HEIGHT, width=WIDTH, theme=theme)
        self.ui_settings = pm.Menu(title="UI Settings", height=HEIGHT, width=WIDTH, theme=theme)

        # Main Menu UI
        self.main_menu.clear()
        self.main_menu._theme.widget_alignment = pm.locals.ALIGN_CENTER
        self.main_menu.add.button(title="Play Now", action=self.game_settings, padding=(base * 0.03, base * 0.0525),
                                  font_color=BLACK, background_color=WHITE, selection_color=BLACK)
        self.main_menu.add.label(title='')
        self.main_menu.add.button(title="Replay", action=self.replay_settings, padding=(base * 0.03, base * 0.075),
                                  font_color=BLACK, background_color=WHITE, selection_color=BLACK)
        self.main_menu.add.label(title='')
        self.main_menu.add.button(title="UI Settings", action=self.ui_settings, padding=(base * 0.03, base * 0.0375),
                                  font_color=BLACK, background_color=WHITE, selection_color=BLACK)

        # Game Settings UI
        self.game_settings._theme.widget_alignment = pm.locals.ALIGN_LEFT
        game_mode = [("Human vs. AI", 1),
                     ("AI vs. AI", 2),
                     ("AI vs. Human", 3)]
        self.game_settings.add.dropselect(title="Game Mode", dropselect_id='game_mode',
                                          items=game_mode, default=0)
        self.game_settings.add.label(title='')
        self.game_settings.add.toggle_switch(title="Game recording", toggleswitch_id="is_recording", default=False)
        self.game_settings.add.label(title='')
        self.game_settings.add.button(title="Next", action=self.func_settings, padding=base * 0.03,
                                      font_color=BLACK, background_color=WHITE, selection_color=BLACK,
                                      align=pm.locals.ALIGN_CENTER)
        
        # Function Selection UI
        self.func_settings._theme.widget_alignment = pm.locals.ALIGN_LEFT
        eval_func = [("Random Move", None)]
        eval_func.extend(getmembers(heuristics, isfunction))
        eval_func = list(filter(lambda option: option[0][0] != '_', eval_func))
        depth = [(str(num), num) for num in range(1, 6)]
        self.func_settings.add.dropselect(title="Black AI's Evaluating Function", dropselect_id='AI_black_func',
                                          items=eval_func, default=0)
        self.func_settings.add.label(title='')
        self.func_settings.add.selector(title="Depth\t", items=depth, selector_id="AI_black_func_depth", default=2)
        self.func_settings.add.label(title='')
        self.func_settings.add.dropselect(title="White AI's Evaluating Function", dropselect_id='AI_white_func',
                                          items=eval_func, default=0)
        self.func_settings.add.label(title='')
        self.func_settings.add.selector(title="Depth\t", items=depth, selector_id="AI_white_func_depth", default=2)
        self.func_settings.add.label(title='')
        self.func_settings.add.button(title="Game On", action=self.game_start, padding=base * 0.03,
                                      font_color=BLACK, background_color=GREEN, selection_color=WHITE,
                                      align=pm.locals.ALIGN_CENTER)

        # Replay Settings UI
        game_files = os.listdir('game_records')
        game_files = list(filter(lambda file: file[-3:] == '.py', game_files))
        game_files = list(map(lambda tup: (tup[1], tup[0]), enumerate(game_files)))
        self.replay_settings.add.clock(clock_format="%d-%m-%y %H:%M:%S", title_format="Local Time : {0}")
        self.replay_settings.add.label(title='')
        self.replay_settings.add.dropselect(title='Game File', dropselect_id='game_file', items=game_files,
                                            selection_box_height=int(self.replay_settings.get_height() * 0.3),
                                            selection_box_width=int(self.replay_settings.get_width() * 0.5),
                                            default=len(game_files) - 1)
        self.replay_settings.add.label(title='')
        self.replay_settings.add.button(title="Replay Game", action=self.replay_start, padding=base * 0.03,
                                        font_color=BLACK, background_color=GREEN, selection_color=WHITE,
                                        align=pm.locals.ALIGN_CENTER)

        # UI Settings UI(?)
        self.ui_settings.add.range_slider(title="Window's Height", default=600, range_values=(500, 800),
                                          increment=10, value_format=lambda x: str(int(x)), rangeslider_id="height")
        self.ui_settings.add.label(title='')
        self.ui_settings.add.toggle_switch(title="I'm Feeling Lucky", toggleswitch_id="random_sprite", default=False)
        self.ui_settings.add.label(title='')
        self.ui_settings.add.button(title="Apply", action=self.ui_change, padding=base * 0.03,
                                    font_color=BLACK, background_color=GREEN, selection_color=WHITE,
                                    align=pm.locals.ALIGN_CENTER)

        # Inherited data to Othello
        self.settings_data = None
        self.height = base
        self.random_sprite = False

    def run(self):
        self.main_menu.mainloop(self.screen)
        return self.settings_data

    def reselect(self):
        self.main_menu.enable()

    def restart(self):
        self.main_menu.reset(2)
        self.main_menu.enable()

    def game_start(self):
        game_data = self.game_settings.get_input_data()
        func_data = self.func_settings.get_input_data()
        game_mode = game_data['game_mode'][0][1]
        is_recording = game_data['is_recording']
        AI_black_func = func_data['AI_black_func'][0][1]
        AI_black_func_depth = func_data['AI_black_func_depth'][0][1]
        AI_white_func = func_data['AI_white_func'][0][1]
        AI_white_func_depth = func_data['AI_white_func_depth'][0][1]
        self.settings_data = (game_mode, is_recording, (AI_black_func, AI_black_func_depth),
                              (AI_white_func, AI_white_func_depth), None)
        self.main_menu.disable()

    def replay_start(self):
        data = self.replay_settings.get_input_data()
        game_file = f'game_records/{data['game_file'][0][0]}'
        self.settings_data = (0, False, None, None, game_file)
        self.main_menu.disable()

    def ui_change(self):
        data = self.ui_settings.get_input_data()
        new_height = data['height']
        new_height = int((new_height // 10) * 10)
        new_width = new_height * (4 / 3)
        increase = new_height / self.main_menu.get_height()

        pygame.display.set_mode((new_width, new_height))

        self.main_menu.resize(width=new_width, height=new_height)
        for widget in self.main_menu.get_widgets():
            widget.resize(width=widget.get_width() * increase, height=widget.get_height() * increase)

        for menu in self.main_menu.get_submenus(recursive=True):
            menu.resize(width=new_width, height=new_height)
            for widget in menu.get_widgets():
                try:
                    widget.resize(width=widget.get_width() * increase, height=widget.get_height() * increase)
                except:
                    widget.update_font({'size': int(new_height * 0.04)})

        self.height = new_height
        self.random_sprite = data['random_sprite']


# Testing
def main():
    game_prompt = Prompt()
    tup = game_prompt.run()
    print(tup)

    pygame.quit()


if __name__ == "__main__":
    main()
