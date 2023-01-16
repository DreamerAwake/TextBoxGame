import gui

class GUIInventoryScreen:
    """The screen that manages the inventory, and allows the player to review their items."""
    def __init__(self, controller_object, settings_object, character_object):
        self.settings = settings_object  # Store the settings container
        self.character = character_object  # Store the character attributes container
        self.controller = controller_object  # Store the controls container

        self.gui_bg, self.render_surface = self._init_surfaces()

    def _init_surfaces(self):
        """Creates the surfaces needed by the gui and returns them."""
        gui_bg = gui.init_bg_surface(self.settings, "images/gui/debug_gui_winbg.png")

        render_surface = gui_bg.copy()

        return gui_bg, render_surface

    def draw(self):
        """Draws the whole gui panel to self.render_surface."""
        self.render_surface.blit(self.gui_bg, (0, 0))
