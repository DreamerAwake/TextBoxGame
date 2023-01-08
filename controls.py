import sys

import pygame.event


class Controller:
    """Provides for player controls and processing."""
    def __init__(self, settings_object):
        self.settings = settings_object
        self.screen_render_offset_ratio = self.settings.render_surface_size[0] / self.settings.screen_surface_size[0]
        self.controls_enabled = False

        self._init_control_variables()

    def _init_control_variables(self):
        """Initializes the control variables to None"""
        self.last_lmb_down = None
        self.last_lmb_up = None

    def update(self):
        """Updates for a single frame of player control."""

        # Checks the pygame event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Handles Quits
                sys.exit()
            elif self.controls_enabled:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:    # Handles left mouse clicks
                    self.last_lmb_down = (event.pos[0] * self.screen_render_offset_ratio, event.pos[1] * self.screen_render_offset_ratio)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:      # Handles left mouse clicks
                    self.last_lmb_up = (event.pos[0] * self.screen_render_offset_ratio, event.pos[1] * self.screen_render_offset_ratio)

    def disable(self):
        """Disables the controls and empties any stored control data."""
        self.controls_enabled = False
        self._init_control_variables()

    def enable(self):
        """Enables player control."""
        self.controls_enabled = True

    def click_detect_group(self, sprite_group, check_button_down=True, check_button_up=True, acknowledge=True, offset=(0, 0)):
        """Detects if any of the sprites in the group has been clicked. Returns the sprite clicked, or None if there was
         no result found. Can check either or both of button-down and button-up events. If acknowledge is True, then
         the last click is reset to None, to prevent 'phantom clicks' on the space in the future. The offset is an (x,y)
         offset for click detection, it will subtract this amount from the x,y values of the click before checking
         hit detection. This offset should usually be the .topleft of the rect the buttons are rendered in."""

        for each_sprite in sprite_group:

            if self.last_lmb_down and check_button_down:
                # Adjust for the offset
                offset_lmb_down = (self.last_lmb_down[0] - offset[0], self.last_lmb_down[1] - offset[1])
                if each_sprite.rect.collidepoint(offset_lmb_down):
                    if acknowledge:
                        self.last_lmb_down = None
                    return each_sprite

            elif self.last_lmb_up and check_button_up:
                # Adjust for the offset
                offset_lmb_up = (self.last_lmb_down[0] - offset[0], self.last_lmb_down[1] - offset[1])
                if each_sprite.rect.collidepoint(offset_lmb_up):
                    if acknowledge:
                        self.last_lmb_up = None
                    return each_sprite

        return None
