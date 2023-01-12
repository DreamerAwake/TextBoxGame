import random
import pygame

import mypyg
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
        self.gui_bg, self.render_surface, self.sidebar_topics_surface, self.rolling_text_surface, self.header_surface = self._init_surfaces()

        # Initialize the sprite groups
        self.rolling_text_clickable_topics_group = pygame.sprite.Group()
        self.sidebar_topics_group = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        # Initialize the rect for the topic sidebar
        self.sidebar_topics_rect = self.sidebar_topics_surface.get_rect()
        self.sidebar_topics_rect.topleft = (self.settings.render_surface_size[0] * 0.83, self.settings.render_surface_size[1] * 0.08)

        # Initialize the rect for the main text box
        self.rolling_textbox_rect = self.rolling_text_surface.get_rect()
        self.rolling_textbox_focus_rect = self.rolling_textbox_rect.copy()
        self.rolling_textbox_rect.topleft = (self.settings.render_surface_size[0] * 0.01, self.settings.render_surface_size[1] * 0.08)

        # Initialize the rect for the middle response pane
        self.response_pane_rect = pygame.Rect((self.settings.render_surface_size[0] * 0.5, self.settings.render_surface_size[1] * 0.08),
                                              (self.settings.render_surface_size[0] * 0.29, self.settings.render_surface_size[1] * 0.61))

        # Initialize the rect for the header pane
        self.header_rect = self.header_surface.get_rect()
        self.header_rect.centerx = self.settings.render_surface_size[0] * 0.5

        # Create the scene event parser
        self.event_parser = scene_parser.SceneParser(initial_scene_script)

        # Create the text handler.
        self.words = []  #Contains the list of individual words to be written to the text box in the coming frames.
        self.is_writing_text = True
        self.is_bold = False
        self.is_italics = False
        self.last_placed_text_rect = pygame.Rect((self.settings.paragraph_tab_width, 0), self.settings.font_text_body.size("l"))

        # Initialize the topics sidebar
        self._init_topic_sidebar()

    def _init_surfaces(self):
        """Initializes and returns the surfaces needed by the constructor."""
        # BG image for the GUI pane
        gui_bg = self._init_bg_surface("images/gui/debug_gui_winbg.png")

        # The primary render surface for this GUI pane
        render_surface = gui_bg.copy()

        # The surface for the topic-selector sidebar
        sidebar_topics_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.16, self.settings.render_surface_size[1] * 0.71))
        sidebar_topics_surface.fill(self.settings.dynamic_colors["transparency"])
        sidebar_topics_surface.set_colorkey(self.settings.dynamic_colors["transparency"])

        # The surface for the main text box
        rolling_text_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.39, self.settings.render_surface_size[1] * 0.71))
        rolling_text_surface.fill(self.settings.dynamic_colors["transparency"])
        rolling_text_surface.set_colorkey(self.settings.dynamic_colors["transparency"])

        # The surface for the scene title header
        header_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.98, self.settings.render_surface_size[1] * 0.07))
        header_surface.fill(self.settings.dynamic_colors["transparency"])
        header_surface.set_colorkey(self.settings.dynamic_colors["transparency"])

        return gui_bg, render_surface, sidebar_topics_surface, rolling_text_surface, header_surface

    def _init_bg_surface(self, bg_file_path):
        """Takes a filepath and returns the gui_bg surface loaded from that path,
        colored to match the current dynamic color style."""

        gui_bg = pygame.Surface((32, 18))

        gui_bg.blit(pygame.image.load(bg_file_path), (0, 0))

        # Create the pixel array
        pixel_array = pygame.PixelArray(gui_bg)

        # Recolor the pixels
        pixel_array.replace((0, 0, 0), self.settings.dynamic_colors["bg_dark"])
        pixel_array.replace((127, 127, 127), self.settings.dynamic_colors["bg_midtone_dark"])
        pixel_array.replace((195, 195, 195), self.settings.dynamic_colors["bg_midtone_light"])
        pixel_array.replace((255, 255, 255), self.settings.dynamic_colors["bg_light"])

        # Close the array
        pixel_array.close()

        return pygame.transform.scale(gui_bg, self.settings.render_surface_size)

    def _init_topic_sidebar(self):
        """Initializes the topic sidebar for rendering."""
        self.fill_sidebar_topics()
        self.sort_sidebar_topics()

    def _render_header_surface(self):
        """Renders the header surface with the header text."""
        self.header_surface.fill(self.settings.dynamic_colors["transparency"])

        rendered_text = self.settings.font_heading_1.render(self.event_parser.current_event_header, False, self.settings.dynamic_colors["header_text"], self.settings.dynamic_colors["transparency"])
        rendered_text_rect = rendered_text.get_rect()
        rendered_text_rect.centery = self.header_rect.height * 0.5

        self.header_surface.blit(rendered_text, rendered_text_rect)

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

        # If the event has the silent command, skip placing the button
        elif "silent" in self.event_parser.current_event.commands:
            self.set_event_markers()

            self.is_writing_text = True
            self.controller.disable()

            # See if we should give the player items
            give_items(self.event_parser.current_event, self.character.inventory)

            # See if we have checks to run
            if not run_item_checks(self.event_parser, self.character.inventory) and not \
                    run_roll_checks(self.event_parser, self.character.inventory):

                self.event_parser.get_next_event()

            return None  # Used to skip the last block of code in the function, which normally does the opposite of this

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
                                                                          self.settings.dynamic_colors["character_tag"],
                                                                          self.settings.dynamic_colors["transparency"])
            title_text_rect = title_text_render.get_rect()
            title_text_rect.left = 0
            title_text_rect.centery = self.last_placed_text_rect.centery
            self.rolling_text_surface.blit(title_text_render, title_text_rect)

            # Move the last placed text rect, but don't copy this one, it is the wrong size
            self.last_placed_text_rect.right = title_text_rect.right

    def _write_single_word(self):
        """Draws a single word from the words list for the _write_next_word function."""

        # Establish local variables
        next_topic, next_word = self._read_inline_expression(self.words.pop(0))

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
            this_word_render = self.settings.render_text_body_font(next_word, self.settings.dynamic_colors["body_text"], self.is_italics, self.is_bold)
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

            # If unwiped, you may have to clear up old unpicked up items
            elif "clean_up_items" in self.event_parser.current_event.commands:
                self._clean_up_items()

            # Check to see if a character tag needs to be placed.
            if "character" in self.event_parser.current_event.commands:
                self._write_character_tag()

            # Rerender the header in case it has changed
            self._render_header_surface()

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

    def _read_inline_expression(self, expression):
        """Given a string from the _write_single_word function, determines if it has an expression, such as
        a topic or item tag. Then returns the topic object if so. Otherwise returns None."""

        # Check for bold and italics tags
        if expression == "/b":
            self.is_bold = True
            expression = self.words.pop(0)

        elif expression == "/i":
            self.is_italics = True
            expression = self.words.pop(0)

        elif expression == "/":
            self.is_bold = False
            self.is_italics = False
            try:
                expression = self.words.pop(0)
            except IndexError:
                expression = ""

        # Readjust next_word
        next_word = expression

        # Check if the next word is a topic which will be enclosed in <_>
        if "<" in expression:
            # Check if the word needs to be extended to find the rest of the topic.
            while ">" not in expression:
                expression += " " + self.words.pop(0)

            next_word = mypyg.remove_character(expression, '<', '>')
            next_word_truncated = mypyg.remove_character(next_word.lower(), remove_non_alphanumeric=True)

            for each_topic in self.character.topics:
                if next_word_truncated == each_topic.title.lower() or next_word_truncated in each_topic.aliases:
                    return TopicSprite(next_word, each_topic, self, self.rolling_text_clickable_topics_group), next_word

        # Check if the next word is an item which will be enclosed in {_}
        elif "{" in expression:
            # Check if the word needs to be extended to find the rest of the topic.
            while "}" not in expression:
                expression += " " + self.words.pop(0)

            # Split the expression to retrieve arguments
            expression = expression[1:-1]
            arguments = expression.split(",")

            # Check if there is an alias included
            if len(arguments) < 3:
                this_item = self.character.inventory.bag[arguments[0]]
                quantity = int(arguments[1])
            else:
                this_item = self.character.inventory.bag[arguments[1]]
                quantity = int(arguments[2])

            return ItemTopicSprite(arguments[0], this_item, quantity, self, self.rolling_text_clickable_topics_group), next_word

        else:
            return None, next_word

    def _clean_up_items(self):
        """Sets all item topics in the rolling text box to read as already picked up."""
        for each_sprite in self.rolling_text_clickable_topics_group:
            each_sprite.is_picked_up = True
            each_sprite.update()

    def _wipe_rolling_textbox(self):
        """Wipes the rolling text box, 'factory reset'."""

        # Reset the surface for the main text box
        self.rolling_text_surface = pygame.Surface((self.settings.render_surface_size[0] * 0.39, self.settings.render_surface_size[1] * 0.71))
        self.rolling_text_surface.fill(self.settings.dynamic_colors["transparency"])
        self.rolling_text_surface.set_colorkey(self.settings.dynamic_colors["transparency"])

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
            new_rolling_text_surface.fill(self.settings.dynamic_colors["transparency"])
            new_rolling_text_surface.set_colorkey(self.settings.dynamic_colors["transparency"])
            new_rolling_text_surface.blit(self.rolling_text_surface, (0, 0))
            self.rolling_text_surface = new_rolling_text_surface
            self.rolling_textbox_focus_rect.bottom = self.last_placed_text_rect.bottom

    def draw(self):
        """Draws the whole gui panel to self.render_surface."""
        self.render_surface.blit(self.gui_bg, (0, 0))
        self.redraw_rolling_text(draw_ui_bg=False)
        self.redraw_buttons()
        self.redraw_sidebar_topics()
        self.redraw_header()

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
                if each_topic.title in self.event_parser.current_events_script.keys() or each_topic.title in self.event_parser.use_generic_topics:
                    available_topics.append(each_topic)
                else:
                    grayed_out_topics.append(each_topic)

        current_y_position = 0  # will be used to increment button placement

        # Place available topics
        for each_topic in available_topics:
            for each_topic_sprite in self.sidebar_topics_group:
                if each_topic == each_topic_sprite.topic:
                    each_topic_sprite.is_active = True
                    each_topic_sprite.update()
                    each_topic_sprite.rect.top = current_y_position
                    current_y_position += each_topic_sprite.rect.height
                    break

        current_y_position += 50    # Creates a margin between active and inactive buttons

        # Place grayed out topics
        for each_topic in grayed_out_topics:
            for each_topic_sprite in self.sidebar_topics_group:
                if each_topic == each_topic_sprite.topic:
                    each_topic_sprite.is_active = False
                    each_topic_sprite.update()
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
        self.sidebar_topics_surface.fill(self.settings.dynamic_colors["transparency"])
        self.sidebar_topics_group.draw(self.sidebar_topics_surface)
        self.render_surface.blit(self.sidebar_topics_surface, self.sidebar_topics_rect)

    def redraw_header(self):
        """Redraws the scene title header."""
        self.render_surface.blit(self.header_surface, self.header_rect)

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
            self.image = self.settings.render_text_body_font(self.text, self.settings.dynamic_colors["topic_known"], self.gui.is_italics, self.gui.is_bold)
        else:
            self.image = self.settings.render_text_body_font(self.text, self.settings.dynamic_colors["topic_unknown"],
                                                             self.gui.is_italics, self.gui.is_bold)
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
                self.gui.rolling_text_clickable_topics_group.update()

            # Set the scene mark
            self.gui.event_parser.mark_this_event()

            # Get the scene related to the topic
            if self.topic.title in self.gui.event_parser.current_events_script.keys():
                self.gui.event_parser.get_event_at_ID(self.topic.title)
            else:
                self.gui.event_parser.get_event_at_ID("", inject_event=self.topic.event)


class ItemTopicSprite(gui.Button):
    """An in-line topic that gives the player an item"""
    def __init__(self, display_alias, item_object, give_quantity, gui_object, *topic_groups):
        self.text = display_alias
        self.item = item_object
        self.quantity = give_quantity
        self.gui = gui_object

        self.is_picked_up = False

        super().__init__(gui_object.settings, *topic_groups)

    def _init_image(self):
        """Draws the image for the button and saves it as the self.image."""
        if self.is_picked_up:
            self.image = self.settings.render_text_body_font(self.text, self.settings.dynamic_colors["dull_text"],
                                                             self.gui.is_italics, self.gui.is_bold)

        else:
            self.image = self.settings.render_text_body_font(self.text, self.settings.dynamic_colors["inline_item"],
                                                             self.gui.is_italics, self.gui.is_bold)

    def draw(self, target_surface):
        """Draws the rendered topic to the surface"""
        self._init_image()
        target_surface.blit(self.image, self.rect)

    def update(self):
        self._init_image()

    def on_click(self):
        """Gives the player the item and toggles the item topic off."""
        if not self.is_picked_up:
            self.gui.character.inventory.add(self.item.name, self.quantity)
            self.is_picked_up = True
            self._init_image()


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
            self.image = self.settings.font_UI_text.render(self.text, True, self.settings.dynamic_colors["topic_known"], self.settings.dynamic_colors["transparency"])
        else:
            self.image = self.settings.font_UI_text.render(self.text, True, self.settings.dynamic_colors["dull_text"], self.settings.dynamic_colors["transparency"])

    def draw(self, target_surface):
        """Draws the rendered topic to the surface"""
        self._init_image()
        target_surface.blit(self.image, self.rect)

    def update(self):
        self._init_image()

    def on_click(self):
        """Starts the topic event in the parser's event list. Sets the necessary flags."""
        if self.is_active:

            # Check if the event parser has enabled topic selection
            if self.gui.event_parser.enable_topics:

                # Set variables to prepare for the next pass of text writing
                self.gui.is_writing_text = True
                self.gui.controller.disable()

                # Set the scene mark if one needs to be present
                self.gui.event_parser.mark_this_event()

                # Get the scene related to the topic
                if self.topic.title in self.gui.event_parser.use_generic_topics:
                    self.gui.event_parser.get_event_at_ID("", inject_event=self.topic.event)
                else:
                    self.gui.event_parser.get_event_at_ID(self.topic.title)


class ContinueButton(gui.Button):
    """A basic continue button for progressing a 'text' type event."""
    def __init__(self, parent_gui, center_position):
        self.gui = parent_gui
        super().__init__(self.gui.settings, self.gui.buttons_group, position=center_position, use_center_position=True)

    def _render_text(self):
        """Renders the text for the image initializer"""
        rendered_text = self.settings.font_UI_text.render("Continue", True, self.settings.dynamic_colors["body_text"], self.settings.dynamic_colors["bg_midtone_light"])
        return rendered_text, rendered_text.get_rect()

    def _init_image(self):
        # Render the text that is the base of the button shape
        rendered_text, text_rect = self._render_text()

        # Create the button surface and fill it black
        self.image = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
        self.image.fill(self.settings.dynamic_colors["bg_dark"])

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

        # See if we should give the player items
        give_items(self.gui.event_parser.current_event, self.gui.character.inventory)

        # See if we have checks to run
        if not run_item_checks(self.gui.event_parser, self.gui.character.inventory) and not \
                run_roll_checks(self.gui.event_parser, self.gui.character.inventory):

            self.gui.event_parser.get_next_event()


class ChoiceButton(ContinueButton):
    """A choice button for making choices presented by the script."""
    def __init__(self, parent_gui, center_position, choice_text):
        self.text = choice_text
        super().__init__(parent_gui, center_position)

    def _render_text(self):
        # Render the text that is the base of the button shape
        rendered_text = self.settings.font_UI_text.render(self.text, True, self.settings.dynamic_colors["body_text"], self.settings.dynamic_colors["bg_midtone_light"])
        return rendered_text, rendered_text.get_rect()

    def on_click(self):
        """Starts the chosen event from the parser's event list. Sets the necessary flags."""
        self.gui.set_event_markers()

        self.gui.is_writing_text = True
        self.gui.buttons_group.empty()
        self.gui.controller.disable()

        self.gui.event_parser.get_event_at_ID(self.gui.event_parser.current_event.choices[self.text])


def give_items(event, inventory):
    """Gives the player items based on the event's give_item details.
    Returns True if there is a give item command, False otherwise."""

    # Check if there is a give_item command
    if "give_item" in event.commands:
        # Give the item
        inventory.add(event.give_item_name, event.give_item_quantity)


def run_item_checks(event_parser, inventory):
    """Checks if the player has the specified number of items to pass the event,
    or else sends the player to the fail event. Returns True if there is a check event, False otherwise."""

    event = event_parser.current_event

    # Check if there is an item_check
    if event.check_item_quantity:
        # Run the item check
        if inventory.bag[event.check_item_name].stock and inventory.bag[event.check_item_name].stock >= event.check_item_quantity:
            event_parser.get_next_event()
            return True
        else:
            event_parser.get_event_at_ID(event.on_fail_event_ID)
            return True

    return False


def run_roll_checks(event_parser, inventory):
    """Runs a random roll for the current event. Returns True if there is a roll event, False otherwise."""
    event = event_parser.current_event

    # Check if there is a roll_check
    if event.check_roll_difficulty:
        print("Rolling check")
        print(f"Difficulty {event.check_roll_difficulty}, Roll Range 1-{event.check_roll_range}")
        # Run the roll_check
        random_number = random.randint(1, event.check_roll_range)
        print(f'Number "on-the-dice": {random_number}')
        # Add item modifiers
        try:
            random_number += inventory.bag[event.check_item_name].stock
        except TypeError:
            pass
        print(f"Final total: {random_number}")
        if random_number >= event.check_roll_difficulty:
            event_parser.get_next_event()
        else:
            event_parser.get_event_at_ID(event.on_fail_event_ID)

        return True

    return False


if __name__ == "__main__":
    settings_object = settings.Settings()
    character_object = character.CharacterProfile()
    controller_object = controls.Controller(settings_object)
    try:
        new_panel = GUIAdventureScreen(controller_object, settings_object, character_object, "scenes/INTRO.scn")
    except FileNotFoundError:
        new_panel =GUIAdventureScreen(controller_object, settings_object, character_object)

    while True:
        new_panel.update()
        new_panel.draw()
        settings_object.display_surface.blit(pygame.transform.smoothscale(new_panel.render_surface, settings_object.screen_surface_size), (0, 0))
        pygame.display.flip()
