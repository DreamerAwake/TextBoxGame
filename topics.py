import csv

import scene_parser


class Topic:
    """A top level class for Topic Objects. Topics inherit from this. Can also be used to generate nonce topics with no
    special properties other than the baseline functionality of topics."""
    def __init__(self, topic_string_exact, topic_generic_response, *topic_aliases, is_known_topic=False):
        self.title = topic_string_exact
        self.event = self._init_topic_event(topic_generic_response)
        self.aliases = topic_aliases

        self.is_known_topic = is_known_topic

    def _init_topic_event(self, topic_response):
        """Creates the event that runs when the generic response is used."""
        this_event = ((self.title, topic_response, "return", ""), ())

        return scene_parser.SceneEvent(this_event, 0)

def init_topics(topic_filename):
    """Initialize a list of all topics. Any new topics MUST
    be added to this list or they will not appear anywhere in the game."""
    # Open the topics file and write it to a python list
    unparsed_topic_list = []

    with open(topic_filename, newline='', encoding='UTF-8') as topicfile:
        topic_csv_reader = csv.reader(topicfile)
        for each_line in topic_csv_reader:
            unparsed_topic_list.append(each_line)

    # Convert the topic list to objects
    topics = []

    for each_line in unparsed_topic_list:
        # Check if the topic should be known from the start
        if "is_known" in each_line[3]:
            is_known_topic = True
        else:
            is_known_topic = False

        topic_aliases = each_line[1].split(", ")

        topics.append(Topic(each_line[0], each_line[2], *topic_aliases, is_known_topic=is_known_topic))

    return topics
