import pygame
import scene_parser
import controls
import settings
import character
import gui


class GUIAdventureScreen:
    """The primary gameplay screen. Takes input from a scene parser and outputs the basic gameplay loop of displaying
    text and then waiting for player input."""
    def __init__(self, controller_object, settings_object, character_object, initial_scene_script="scenes/EXAMPLE.csv"):
        self.settings = settings_object  # Store the settings container
        self.character = character_object  # Store the character attributes container
        self.controller = controller_object  # Store the controls container

        # Initialize render surfaces
        self.gui_bg, self.render_surface, self.sidebar_topics_surface, self.rolling_text_surface = self._init_surfaces()

        # Initialize the sprite groups
        self.rolling_text_clickable_topics_group = pygame.sprite.Group()
        self.sidebar_topics_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        # Initialize the rect for the topic sidebar
        self.sidebar_topics_rect = self.sidebar_topics_surface.get_rect()
        self.sidebar_topics_rect.topleft = (self.settings.render_surface_size[0] * 0.76, self.settings.render_surface_size[1] * 0.08)

        # Initialize the rect for the main text box
        self.rolling_textbox_rect = self.rolling_text_surface.get_rect()
        self.rolling_textbox_focus_rect = self.rolling_textbox_rect.copy()
        self.rolling_textbox_rect.topleft = (self.settings.render_surface_size[0] * 0.35, self.settings.render_surface_size[1] * 0.08)

        # Initialize the rect for the bottom response pane
        self.response_pane_rect = pygame.Rect((self.settings.render_surface_size[0] * 0.34, self.settings.render_surface_size[1] * 0.80),
                                              (self.settings.render_surface_size[0] * 0.66, self.settings.render_surface_size[1] * 0.20))

        # Create the scene event parser
        self.event_parser = scene_parser.SceneParser(initial_scene_script)

        # Create the text handler.
        self.words = []  #Contains the list of individual words to be written to the text box in the coming frames.
        self.is_writing_text = True
        self.last_placed_text_rect = pygame.Rect((self.settings.paragraph_tab_width, 0), self.settings.font_text_body.size("l"))

        # Initialize the topics sidebar
        self._init_topic_sidebar()

    def _init_surfaces(self):
        """Initializes and returns the surfaces needed by the constructor."""
        # BG image for the GUI pane
        gui_bg = pygame.transform.smoothscale(pygame.image.load("images/gui/adventure_screen_winbg.png"), self.settings.render_surface_size)

        # The primary render surface for this GUI pane
        render_surface = gui_bg.copy()

        # The surface for the topic-selector sidebar
        sidebar_topics_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.23, self.settings.render_surface_size[1] * 0.71))
        sidebar_topics_surface.fill(self.settings.colors["transparency"])
        sidebar_topics_surface.set_colorkey(self.settings.colors["transparency"])

        # The surface for the main text box
        rolling_text_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.39, self.settings.render_surface_size[1] * 0.71))
        rolling_text_surface.fill(self.settings.colors["transparency"])
        rolling_text_surface.set_colorkey(self.settings.colors["transparency"])

        return gui_bg, render_surface, sidebar_topics_surface, rolling_text_surface

    def _init_topic_sidebar(self):
        """Initializes the topic sidebar for rendering."""
        self.fill_sidebar_topics()
        self.sort_sidebar_topics()

    def _end_event(self):
        """Runs the code that displays buttons at the end of an event."""
        # If the event is a choice now is the time to display the option buttons.
        if "choice" in self.event_parser.current_event.commands:
            # Calculate the spacing for the choice buttons
            button_vertical_spacing = self.response_pane_rect.height / (
                    1 + len(self.event_parser.current_event.choices))
            button_vertical_offset = button_vertical_spacing

            # Create all the choice buttons, placing them and incrementing the offset
            for each_choice in self.event_parser.current_event.choices.keys():
                ChoiceButton(self, (
                    self.response_pane_rect.centerx, self.response_pane_rect.top + button_vertical_offset),
                             each_choice)
                button_vertical_offset += button_vertical_spacing

        # If the event is text now is the time to display the continue button.
        else:
            ContinueButton(self, self.response_pane_rect.center)

        self.is_writing_text = False
        self.controller.enable()

    def _write_character_tag(self):
        """Draws the character tag when applicable. Must be applied before a new line is written."""
        if not self.event_parser.suppress_text:
            # Build the string to render
            title_text_string = self.event_parser.current_event.said_by_character.upper() + " -  "

            # Create the render and the rects
            title_text_render = self.settings.font_text_small_caps.render(title_text_string, True,
                                                                          self.settings.colors["dark blue"],
                                                                          self.settings.colors["transparency"])
            title_text_rect = title_text_render.get_rect()
            title_text_rect.left = 0
            title_text_rect.centery = self.last_placed_text_rect.centery
            self.rolling_text_surface.blit(title_text_render, title_text_rect)

            # Move the last placed text rect, but don't copy this one, it is the wrong size
            self.last_placed_text_rect.right = title_text_rect.right

    def _write_single_word(self):
        """Draws a single word from the words list for the _write_next_word function."""

        # Establish local variables
        next_word = self.words.pop(0)
        next_topic = None

        # Check if the next word is a topic which will be enclosed in <_>
        if "<" in next_word:
            # Check if the word needs to be extended to find the rest of the topic.
            while ">" not in next_word:
                next_word += " " + self.words.pop(0)

            next_word = remove_character(next_word, '<', '>')
            next_word_truncated = remove_character(next_word.lower(), remove_non_alphanumeric=True)

            for each_topic in self.character.topics:
                if next_word_truncated == each_topic.title.lower() or next_word_truncated in each_topic.aliases:
                    next_topic = TopicSprite(next_word, each_topic, self, self.rolling_text_clickable_topics_group)

        # Check that we don't need a new line for this word, if we do, adjust self.last_placed_text_rect
        if self.settings.font_text_body.size(" " + next_word)[0] + self.last_placed_text_rect.right > \
                self.settings.render_surface_size[0] * 0.39:
            self.last_placed_text_rect.right = 0
            self.last_placed_text_rect.top = self.last_placed_text_rect.bottom

            # If the text rect would run off of the rolling box, extend the surface
            self._extend_rolling_text_surface()

        # Put the next word on the rolling display, using topic functionality if it is a topic and manually otherwise
        if next_topic:
            next_topic.rect.left = self.last_placed_text_rect.right + self.settings.font_text_body.size(" ")[0]
            next_topic.rect.bottom = self.last_placed_text_rect.bottom
            next_topic.draw(self.rolling_text_surface)
            self.last_placed_text_rect = next_topic.rect.copy()

        else:
            this_word_render = self.settings.font_text_body.render(next_word, True, self.settings.colors["black"],
                                                                   self.settings.colors["transparency"])
            this_word_rect = this_word_render.get_rect()
            this_word_rect.left = self.last_placed_text_rect.right + self.settings.font_text_body.size(" ")[0]
            this_word_rect.bottom = self.last_placed_text_rect.bottom
            self.rolling_text_surface.blit(this_word_render, this_word_rect)
            self.last_placed_text_rect = this_word_rect

    def _write_next_word(self):
        """Draw the next word in the rolling text box. Returns False if it is done writing
        the current scene text and display buttons, True while writing is still ongoing."""

        # Check to see if the current text from the event has been split, split it if not
        if self.is_writing_text and not self.words:
            self.words = self.event_parser.current_event.text.split()

            # Wipe the rolling text box before writing if the event has the wipe command.
            if "wipe" in self.event_parser.current_event.commands:
                self._wipe_rolling_textbox()

            # Check to see if a character tag needs to be placed.
            if "character" in self.event_parser.current_event.commands:
                self._write_character_tag()

        # If the event is suppressing text, skip rendering and end the event.
        elif self.words and self.event_parser.suppress_text:
            self.words.clear()

            self.event_parser.suppress_text = False

            self._end_event()

        # If there are words in the list, write them
        elif self.words:

            self._write_single_word()

            if not self.words and self.is_writing_text:

                # Move the text rect to the next line
                self.last_placed_text_rect.top = self.last_placed_text_rect.bottom
                self.last_placed_text_rect.right = self.settings.paragraph_tab_width
                self._extend_rolling_text_surface()

                self._end_event()

        return self.is_writing_text

    def _wipe_rolling_textbox(self):
        """Wipes the rolling text box, 'factory reset'."""

        # Reset the surface for the main text box
        self.rolling_text_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.39, self.settings.render_surface_size[1] * 0.71))
        self.rolling_text_surface.fill(self.settings.colors["transparency"])
        self.rolling_text_surface.set_colorkey(self.settings.colors["transparency"])

        # Reset variables for the textbox
        self.rolling_textbox_focus_rect.top = 0
        self.last_placed_text_rect.top = 0
        self.last_placed_text_rect.right = self.settings.paragraph_tab_width

        # Empty the rolling topic group
        self.rolling_text_clickable_topics_group.empty()

    def _extend_rolling_text_surface(self):
        """Extends the rolling text surface to accommodate new text."""
        if self.last_placed_text_rect.bottom > self.rolling_text_surface.get_height():
            new_rolling_text_surface = pygame.Surface(
                (self.rolling_text_surface.get_width(), self.last_placed_text_rect.bottom))
            new_rolling_text_surface.fill(self.settings.colors["transparency"])
            new_rolling_text_surface.set_colorkey(self.settings.colors["transparency"])
            new_rolling_text_surface.blit(self.rolling_text_surface, (0, 0))
            self.rolling_text_surface = new_rolling_text_surface
            self.rolling_textbox_focus_rect.bottom = self.last_placed_text_rect.bottom

    def draw(self):
        """Draws the whole gui panel to self.render_surface."""
        self.render_surface.blit(self.gui_bg, (0, 0))
        self.redraw_rolling_text(draw_ui_bg=False)
        self.redraw_buttons()
        self.redraw_sidebar_topics()

    def add_to_sidebar_topics(self, topic_object):
        """Adds the given topic object to the sidebar as a topic sprite."""
        SidebarTopicSprite(topic_object.title, topic_object, self, self.sidebar_topics_group)

    def fill_sidebar_topics(self):
        """Adds all of the currently known topics to the sidebar group. Does not place them."""
        for each_topic in self.character.topics:
            if each_topic.is_known_topic:
                SidebarTopicSprite(each_topic.title, each_topic, self, self.sidebar_topics_group)

    def sort_sidebar_topics(self):
        """Sorts the positions of the sidebar topics in the sprite group and sets their is_active states."""
        available_topics = []
        grayed_out_topics = []

        # Pull from the list of all topics a list of topics in the scene you already know, and also all other known topics
        for each_topic in self.character.topics:
            if each_topic.is_known_topic:
                if each_topic.title in self.event_parser.current_events_script.keys():
                    available_topics.append(each_topic)
                else:
                    grayed_out_topics.append(each_topic)

        current_y_position = 0  # will be used to increment button placement

        # Place available topics
        for each_topic in available_topics:
            for each_topic_sprite in self.sidebar_topics_group:
                if each_topic == each_topic_sprite.topic:
                    each_topic_sprite.is_active = True
                    each_topic_sprite.rect.top = current_y_position
                    current_y_position += each_topic_sprite.rect.height
                    break

        current_y_position += 50    # Creates a margin between active and inactive buttons

        # Place grayed out topics
        for each_topic in grayed_out_topics:
            for each_topic_sprite in self.sidebar_topics_group:
                if each_topic == each_topic_sprite.topic:
                    each_topic_sprite.is_active = False
                    each_topic_sprite.rect.top = current_y_position
                    current_y_position += each_topic_sprite.rect.height
                    break

    def set_event_markers(self):
        """Sets the event markers. Should only be called once per event."""
        # Check if a clear_marks or forget_mark command are present.
        if "clear_marks" in self.event_parser.current_event.commands:
            self.event_parser.clear_marked_events()

        elif "forget_mark" in self.event_parser.current_event.commands:
            self.event_parser.clear_marked_events(1)

        # Set the scene mark if one needs to be present
        if "mark" in self.event_parser.current_event.commands:
            self.event_parser.mark_this_event()

    def redraw_rolling_text(self, draw_ui_bg=True):
        """Redraw the rolling text box."""
        # Redraw Background UI
        if draw_ui_bg:
            self.render_surface.blit(self.gui_bg, self.rolling_textbox_rect, self.rolling_textbox_rect)

        self.rolling_text_clickable_topics_group.draw(self.rolling_text_surface)

        # Redraw the text
        self.render_surface.blit(self.rolling_text_surface, self.rolling_textbox_rect, self.rolling_textbox_focus_rect)

    def redraw_response_pane(self):
        """Redraws the response pane and all its buttons."""
        self.render_surface.blit(self.gui_bg, self.response_pane_rect, self.response_pane_rect)

    def redraw_buttons(self):
        """Redraws all of the buttons"""
        self.buttons_group.draw(self.render_surface)

    def redraw_sidebar_topics(self):
        """Redraws the sidebar containing the player's known topics."""
        self.render_surface.blit(self.gui_bg, self.sidebar_topics_rect, self.sidebar_topics_rect)
        self.sidebar_topics_group.draw(self.sidebar_topics_surface)
        self.render_surface.blit(self.sidebar_topics_surface, self.sidebar_topics_rect)

    def update(self):
        """Called once per frame."""
        self.controller.update()  # Update the controls, only stores input that then must be used elsewhere

        if not self._write_next_word():
            self.update_controls()

    def update_controls(self):
        """Checks for inputs from the controller and processes them."""
        clicked_button = None
        if self.controller.last_lmb_up:

            # Check the main rolling text box
            if self.rolling_textbox_rect.collidepoint(self.controller.last_lmb_up):
                offset = (self.rolling_textbox_rect.left, self.rolling_textbox_rect.top + self.rolling_textbox_rect.height - self.rolling_text_surface.get_height() )
                clicked_button = self.controller.click_detect_group(self.rolling_text_clickable_topics_group, check_button_down=False, offset=offset)

            # Check the topics sidebar
            elif self.sidebar_topics_rect.collidepoint(self.controller.last_lmb_up):
                clicked_button = self.controller.click_detect_group(self.sidebar_topics_group, check_button_down=False, offset=self.sidebar_topics_rect.topleft)

            # Check global buttons
            else:
                clicked_button = self.controller.click_detect_group(self.buttons_group, check_button_down=False)

        # If a resulting button was found.
        if clicked_button:
            # If one indeed has been clicked, run its on_click function
            clicked_button.on_click()


class TopicSprite(gui.Button):
    """Displays topics as clickable buttons."""
    def __init__(self, display_alias, topic_object, gui_object, *topic_groups):
        self.text = display_alias
        self.topic = topic_object
        self.gui = gui_object

        super().__init__(gui_object.settings, *topic_groups)

    def _init_image(self):
        """Draws the image for the button and saves it as the self.image."""
        if self.topic.is_known_topic:
            self.image = self.settings.font_text_body.render(self.text, True, self.settings.colors["light blue"], self.settings.colors["transparency"])
        else:
            self.image = self.settings.font_text_body.render(self.text, True, self.settings.colors["orange"], self.settings.colors["transparency"])

    def draw(self, target_surface):
        """Draws the rendered topic to the surface"""
        self._init_image()
        target_surface.blit(self.image, self.rect)

    def update(self):
        self._init_image()

    def on_click(self):
        """Starts the topic event in the parser's event list. Sets the necessary flags."""
        # Check if the event parser has enabled topic selection
        if self.gui.event_parser.enable_topics:

            # Set variables to prepare for the next pass of text writing
            self.gui.is_writing_text = True
            self.gui.controller.disable()

            # Check if the topic is unknown
            if not self.topic.is_known_topic:
                self.topic.is_known_topic = True
                self.gui.add_to_sidebar_topics(self.topic)
                self.gui.sort_sidebar_topics()

            # Set the scene mark
            self.gui.event_parser.mark_this_event()

            # Get the scene related to the topic
            self.gui.event_parser.get_event_at_ID(self.topic.title)


class SidebarTopicSprite(gui.Button):
    """Displays topics as clickable buttons."""
    def __init__(self, display_alias, topic_object, gui_object, *topic_groups):
        self.text = display_alias
        self.topic = topic_object
        self.gui = gui_object
        self.is_active = True

        super().__init__(gui_object.settings, *topic_groups)

    def _init_image(self):
        """Draws the image for the button and saves it as the self.image."""
        if self.is_active:
            self.image = self.settings.font_UI_text.render(self.text, True, self.settings.colors["light blue"], self.settings.colors["transparency"])
        else:
            self.image = self.settings.font_UI_text.render(self.text, True, self.settings.colors["gray"], self.settings.colors["transparency"])

    def draw(self, target_surface):
        """Draws the rendered topic to the surface"""
        self._init_image()
        target_surface.blit(self.image, self.rect)

    def update(self):
        self._init_image()

    def on_click(self):
        """Starts the topic event in the parser's event list. Sets the necessary flags."""
        # Check if the event parser has enabled topic selection
        if self.gui.event_parser.enable_topics:

            # Set variables to prepare for the next pass of text writing
            self.gui.is_writing_text = True
            self.gui.controller.disable()

            # Set the scene mark if one needs to be present
            self.gui.event_parser.mark_this_event()

            # Get the scene related to the topic
            self.gui.event_parser.get_event_at_ID(self.topic.title)


class ContinueButton(gui.Button):
    """A basic continue button for progressing a 'text' type event."""
    def __init__(self, parent_gui, center_position):
        self.gui = parent_gui
        super().__init__(self.gui.settings, self.gui.buttons_group, position=center_position, use_center_position=True)

    def _render_text(self):
        """Renders the text for the image initializer"""
        rendered_text = self.settings.font_UI_text.render("Continue", True, self.settings.colors["black"], self.settings.colors["light blue"])
        return rendered_text, rendered_text.get_rect()

    def _init_image(self):
        # Render the text that is the base of the button shape
        rendered_text, text_rect = self._render_text()

        # Create the button surface and fill it black
        self.image = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
        self.image.fill(self.settings.colors["black"])

        # Move the text rect to the middle of the image.
        text_rect.center = self.image.get_rect().center

        # Blit the text to the button image
        self.image.blit(rendered_text, text_rect)

    def on_click(self):
        """Starts the next event in the parser's event list. Sets the necessary flags."""
        self.gui.set_event_markers()

        self.gui.is_writing_text = True
        self.gui.buttons_group.empty()
        self.gui.controller.disable()

        self.gui.event_parser.get_next_event()


class ChoiceButton(ContinueButton):
    """A choice button for making choices presented by the script."""
    def __init__(self, parent_gui, center_position, choice_text):
        self.text = choice_text
        super().__init__(parent_gui, center_position)

    def _render_text(self):
        # Render the text that is the base of the button shape
        rendered_text = self.settings.font_UI_text.render(self.text, True, self.settings.colors["black"], self.settings.colors["light blue"])
        return rendered_text, rendered_text.get_rect()

    def on_click(self):
        """Starts the chosen event from the parser's event list. Sets the necessary flags."""
        self.gui.set_event_markers()

        self.gui.is_writing_text = True
        self.gui.buttons_group.empty()
        self.gui.controller.disable()

        self.gui.event_parser.get_event_at_ID(self.gui.event_parser.current_event.choices[self.text])


def remove_character(source_string, *characters_to_remove, remove_non_alphanumeric=False):
    """Removes the remove_character from a given string and returns that string without those characters.
    If remove_non_alphanumeric is True, it will remove all non letter/number characters from the string,
    except spaces which are left untouched."""
    # If no settings are selected, then return the base string
    if not characters_to_remove and not remove_non_alphanumeric:
        return source_string

    if remove_non_alphanumeric:
        new_string = ""

        # For each character, check if it is alphanumeric, and if so, add it to the new string.
        for each_character in [*source_string]:
            if each_character.isalnum() or each_character == " ":
                new_string += each_character

        return new_string

    if characters_to_remove:
        new_string = ""

        for each_character in [*source_string]:
            if each_character not in characters_to_remove:
                new_string += each_character

        return new_string


if __name__ == "__main__":
    settings_object = settings.Settings()
    character_object = character.CharacterProfile()
    controller_object = controls.Controller(settings_object)
    new_panel = GUIAdventureScreen(controller_object, settings_object, character_object)

    while True:
        new_panel.update()
        new_panel.draw()
        settings_object.display_surface.blit(pygame.transform.smoothscale(new_panel.render_surface, settings_object.screen_surface_size), (0, 0))
        pygame.display.flip()
