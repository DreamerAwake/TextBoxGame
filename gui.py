import pygame.sprite


class Button(pygame.sprite.Sprite):
    """A basic clickable button, used as the base of all button objects."""
    def __init__(self, settings_object, *groups, position=(0, 0), use_center_position=False):
        super().__init__(*groups)
        self.settings = settings_object
        self.image = None
        self._init_image()
        self.rect = self.image.get_rect()
        if use_center_position:
            self.rect.center = position
        else:
            self.rect.topleft = position

    def _init_image(self):
        """Returns a pygame surface for the button's image."""
        self.image = pygame.Surface((50, 50))
        self.image.fill((10, 10, 10))

    def on_click(self):
        """Called when something clicks on the button"""
        pass


def init_bg_surface(settings, bg_file_path):
    """Takes a filepath and returns the gui_bg surface loaded from that path,
    colored to match the current dynamic color style."""

    loaded_image = pygame.image.load(bg_file_path)
    gui_bg = pygame.Surface(loaded_image.get_size())
    gui_bg.blit(loaded_image, (0, 0))

    # Create the pixel array
    pixel_array = pygame.PixelArray(gui_bg)

    # Recolor the pixels
    pixel_array.replace((0, 0, 0), settings.dynamic_colors["bg_dark"])
    pixel_array.replace((64, 64, 64), settings.dynamic_colors["bg_midtone_dark"])
    pixel_array.replace((128, 128, 128), settings.dynamic_colors["bg_midtone_light"])
    pixel_array.replace((255, 255, 255), settings.dynamic_colors["bg_light"])

    # Close the array
    pixel_array.close()

    return pygame.transform.scale(gui_bg, settings.render_surface_size)
