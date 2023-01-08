import csv


class SceneParser:
    """This object reads scenes from files stored as csv data and returns events useable by the reader_screen."""
    def __init__(self, initial_scene_script):
        self.current_events_script = None
        self.current_event = None
        self.current_event_header = None
        self.start_in = None

        self.enable_topics = False
        self.suppress_text = False

        self.marked_events_list = []

        self.read_from_scene(initial_scene_script)

    def _read_topics_enabled(self):
        """Sets the state of enable_topics based on the current event. Defaults to False."""
        if "enable_topics" in self.current_event.commands:
            self.enable_topics = True
        else:
            self.enable_topics = False

    def get_next_event(self):
        """Reads the next event from the current event and loads it."""
        if "scene" in self.current_event.commands:
            self.read_from_scene("scenes/" + self.current_event.next_ID + ".csv")
        elif self.current_event.next_ID == "return":
            self.return_to_last_mark()
        else:
            self.current_event = self.current_events_script[self.current_event.next_ID]
            self._read_topics_enabled()

    def get_event_at_ID(self, ID_code):
        """Gets the event with the given ID in the current scene. Sets it to the current event."""
        self.current_event = self.current_events_script[ID_code]
        self._read_topics_enabled()

    def mark_this_event(self):
        """Marks the current event. The next event with 'return' will jump back to this marked command.
        Marks can be stacked, with the most recent mark being the next returned to."""
        self.marked_events_list.append(self.current_event)

    def clear_marked_events(self, last_X=None):
        """Clears all marked events. If passed an int for last_X, it will delete at least that many of the previous
        commands."""
        if not last_X or (last_X and last_X > len(self.marked_events_list)):
            self.marked_events_list.clear()
        else:
            self.marked_events_list = self.marked_events_list[:-last_X]

    def return_to_last_mark(self):
        """Returns to the last marked event. Clears that last marked event."""
        self.current_event = self.marked_events_list.pop()

        # If there is no 'reread' Command, do not reread the prompt on returning.
        if "reread" not in self.current_event.commands:
            self.suppress_text = True

        self._read_topics_enabled()

    def read_from_scene(self, scene_filename):
        """Reads a scene from a csv file into a list of event commands."""
        # Clear the old event script
        if self.current_events_script:
            self.current_events_script.clear()

        unparsed_event_list = []

        # Open the scene file and write it into a python list
        with open(scene_filename, newline='') as scenefile:
            scene_csv_reader = csv.reader(scenefile)
            for each_line in scene_csv_reader:
                unparsed_event_list.append(each_line)

        # Find stage direction lines from the top of the scene file, process and remove them
        stage_directions = ("HEADER")   # Extend this tuple with other stage directions as you design them

        while unparsed_event_list[0][0] in stage_directions:
            this_stage_direction = unparsed_event_list.pop(0)
            if this_stage_direction[0] == "HEADER":
                self.current_event_header = this_stage_direction[1]
                self.start_in = this_stage_direction[2]

        # Pass through all the rows of the unparsed event list and make event objects for them
        event_dict = {}
        current_row_index = 0

        while current_row_index < len(unparsed_event_list):
            current_event_ID = unparsed_event_list[current_row_index][0]
            # Key the scene ID to the Event object in the dict.
            event_dict[current_event_ID] = SceneEvent(unparsed_event_list, current_row_index)
            # Increment the current row by 1 + the number of extra rows devoted to choices from the last event added
            if event_dict[current_event_ID].choices:
                current_row_index += len(event_dict[current_event_ID].choices) + 1
            else:
                current_row_index += 1

        self.current_events_script = event_dict
        self.get_event_at_ID(self.start_in)  # Loads the first event
        self._read_topics_enabled()


class SceneEvent:
    """Takes the event index and the row list and creates an Event object that can be read by the scene parser."""
    def __init__(self, event_list, event_index_number):
        self.ID = event_list[event_index_number][0]
        self.text = event_list[event_index_number][1]
        self.said_by_character = None
        self.commands, self.choices = self._read_event_commands(event_list, event_index_number)
        self.next_ID = self._read_next_ID(event_list, event_index_number)

        #print(f"Scene: {self.ID} -> {self.next_ID}, with {self.commands}: {self.text}")

    def _read_event_commands(self, event_list, event_index_number):
        """Reads an event from the unparsed event list produced in the scene parser. Returns a list of the commands in
        the event, and a dictionary of choices for choice based events. Always returns a list of events even if it is
        empty, but will return None rather than an empty choice dict."""
        found_commands = []
        event_command_string = event_list[event_index_number][3]

        # Locate and remove any character tags
        if event_command_string and event_command_string[0] == "[":

            character_tag = event_command_string[:event_command_string.index("]") - len(event_command_string)]
            event_command_string = event_command_string[len(character_tag) + 1:]

            self.said_by_character = character_tag[1:]
            found_commands.append("character")

        # Split remaining tags to truncate spaces
        event_command_string = event_command_string.split()

        if not event_command_string:
            return found_commands, None

        # Add command tags
        while event_command_string:
            next_command = event_command_string.pop(0)
            found_commands.append(next_command)

        # If the text is a choice, find the choices.
        choices = {}
        if "choice" in found_commands:

            iterations = 1
            next_choice = event_list[event_index_number + iterations]
            while not next_choice[0]:
                choices[next_choice[1]] = next_choice[2]
                iterations += 1
                next_choice = event_list[event_index_number + iterations]

        if choices:
            return found_commands, choices
        else:
            return found_commands, None

    def _read_next_ID(self, event_list, event_index_number):
        next_ID = event_list[event_index_number][2]

        if next_ID:
            return next_ID
        else:
            try:
                return event_list[event_index_number + 1][0]
            except IndexError:
                return None
