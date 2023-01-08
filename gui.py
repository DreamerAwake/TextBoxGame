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