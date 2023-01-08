import pygame


class Settings:
    """The settings object, which contains all directly alterable settings."""
    def __init__(self):
        # Screen settings
        self.allowed_screen_sizes = [(2560, 1440),
                                     (1920, 1080),
                                     (1280, 720),
                                     (854, 480)]
        self.screen_surface_size = (1920, 1080)
        self.render_surface_size = (2560, 1440)
        self.display_surface = pygame.display.set_mode(self.screen_surface_size)

        # Font Settings
        pygame.font.init()
        self.font_heading_1 = pygame.font.SysFont("georgia", 52)
        self.font_heading_2 = pygame.font.SysFont("sitkasubheading", 36)
        self.font_text_body = pygame.font.SysFont("leelawadeeui", 32)
        self.font_text_small_caps = pygame.font.SysFont("leelawadeeui", 28)
        self.font_UI_text = pygame.font.SysFont("nirmalaui", 36)

        self.paragraph_tab_width = 100
        self.paragraph_spacing_below = 20

        # Color Settings
        self.colors = {"black": pygame.Color(10, 10, 10),
                       "gray": pygame.Color(128, 128, 128),
                       "white": pygame.Color(250, 250, 250),
                       "transparency": pygame.Color(255, 255, 255),
                       "red": pygame.Color(250, 10, 10),
                       "orange": pygame.Color(210, 90, 10),
                       "light blue": pygame.Color(110, 160, 250),
                       "dark blue": pygame.Color(60, 80, 128)}
