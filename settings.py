import csv

import pygame

import mypyg


class Settings:
    """The settings object, which contains all directly alterable settings."""
    def __init__(self):
        # Screen settings
        self.allowed_screen_sizes = [(2560, 1440),
                                     (1920, 1080),
                                     (1280, 720),
                                     (854, 480)]
        self.screen_surface_size = (1280, 720)
        self.render_surface_size = (2560, 1440)
        self.display_surface = pygame.display.set_mode(self.screen_surface_size)

        # Font Settings
        pygame.font.init()
        self.font_heading_1 = pygame.font.SysFont("georgia", 52)
        self.font_heading_2 = pygame.font.SysFont("sitkasubheading", 36)
        self.font_text_body = pygame.font.SysFont("sourcesanspro", 32)
        self.font_text_body_italics = pygame.font.SysFont("sourcesanspro", 32, italic=True)
        self.font_text_body_bold = pygame.font.SysFont("sourcesanspro", 32, bold=True)
        self.font_text_small_caps = pygame.font.SysFont("sourcesanspro", 28)
        self.font_UI_text = pygame.font.SysFont("nirmalaui", 36)

        self.paragraph_tab_width = 100
        self.paragraph_spacing_below = 20

        # Color Settings
        self.color_styles, self.color_keys = self._init_color_styles("scenes/styles.csv")

        self.dynamic_colors = self.get_dynamic_colors("DEFAULT")

    def _init_color_styles(self, styles_filename):
        """Reads the style colors from the .csv into the game."""
        retrieved_color_styles = {}
        retrieved_color_keys = []

        with open(styles_filename, newline='', encoding='UTF-8') as stylefile:
            style_csv_reader = csv.reader(stylefile)

            for each_line in style_csv_reader:

                # Read the line with the dynamic color keys
                if not retrieved_color_keys:

                    each_line.pop(0)  # Corrects for the style name column

                    for each_key in each_line:
                        retrieved_color_keys.append(each_key)

                # Read the style lines
                else:
                    this_style_name = each_line.pop(0)
                    this_style = []

                    for each_color in each_line:
                        each_color = mypyg.remove_character(each_color, remove_non_alphanumeric=True).split()
                        color_tuple = (int(each_color[0]), int(each_color[1]), int(each_color[2]))
                        this_style.append(color_tuple)

                    retrieved_color_styles[this_style_name] = this_style

        return retrieved_color_styles, retrieved_color_keys

    def get_dynamic_colors(self, color_style):
        """Returns a dict of dynamic colors for use by the rendering pipeline. Styles can be swapped by
        passing a new color_style and assigning settings.dynamic_colors to the resulting dict."""
        dynamic_color_dict = {}

        # Set each key in the color_keys to a pygame color of the corresponding tuple
        for each_key, each_color_tuple in zip(self.color_keys, self.color_styles[color_style]):
            dynamic_color_dict[each_key] = pygame.Color(each_color_tuple)
            print(each_key, dynamic_color_dict[each_key])

        return dynamic_color_dict

    def render_text_body_font(self, text, color, italics, bold):
        """Calls renders from text_body_font adjusting for italics and bolds as necessary.
        Returns the rendered text surface."""

        if bold:
            render = self.font_text_body_bold.render(text, True, color, self.dynamic_colors["transparency"])
        elif italics:
            render = self.font_text_body_italics.render(text, True, color, self.dynamic_colors["transparency"])
        else:
            render = self.font_text_body.render(text, True, color, self.dynamic_colors["transparency"])

        return render