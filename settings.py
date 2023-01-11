import pygame


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
        self.colors = {"transparency": pygame.Color(255, 255, 255),
                       "black": pygame.Color(10, 10, 10),
                       "gray": pygame.Color(128, 128, 128),
                       "white": pygame.Color(250, 250, 250),
                       "red": pygame.Color(210, 20, 20),
                       "orange": pygame.Color(210, 90, 10),
                       "yellow": pygame.Color(240, 190, 20),
                       "green": pygame.Color(10, 128, 10),
                       "light blue": pygame.Color(110, 160, 250),
                       "dark blue": pygame.Color(60, 80, 128),
                       "indigo": pygame.Color(128, 20, 240),
                       "pink": pygame.Color(240, 20, 240)
                       }

        self.dynamic_colors = {"header_text": self.colors["dark blue"],
                               "body_text": self.colors["black"],
                               "character_tag": self.colors["dark blue"],
                               "topic_unknown": self.colors["orange"],
                               "topic_known": self.colors["light blue"],
                               "inline_item": self.colors["green"],
                               "dull_text": self.colors["gray"],
                               }

    def render_text_body_font(self, text, color, italics, bold):
        """Calls renders from text_body_font adjusting for italics and bolds as necessary.
        Returns the rendered text surface."""

        if bold:
            render = self.font_text_body_bold.render(text, True, color, self.colors["transparency"])
        elif italics:
            render = self.font_text_body_italics.render(text, True, color, self.colors["transparency"])
        else:
            render = self.font_text_body.render(text, True, color, self.colors["transparency"])


        return render