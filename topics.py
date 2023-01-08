class GenericTopic:
    """A top level class for Topic Objects. Topics inherit from this. Can also be used to generate nonce topics with no
    special properties other than the baseline functionality of topics."""
    def __init__(self, topic_string_exact, *topic_aliases, is_known_topic=False):
        self.title = topic_string_exact
        self.aliases = topic_aliases

        self.is_known_topic = is_known_topic


def init_topics():
    """Initialize a list of all topics. Any new topics MUST
    be added to this list or they will not appear anywhere in the game."""
    # Create the list of topics
    topics = [GenericTopic("The Big One", "the war", "the great war"),
              GenericTopic("crown", "the crown", "king and country"),
              GenericTopic("Dr. Glubberwain", "doctor", "doctor lawrence glubberwain", "dr glubberwain"),
              GenericTopic("Elenore Island", "elenore", "the island"),
              GenericTopic("lighthouse"),
              GenericTopic("On-Farness", "onfarness"),
              GenericTopic("party"),
              GenericTopic("rotten sealife", "rotting sealife"),
              GenericTopic("sailors", "sailor"),
              GenericTopic("topics", "topic"),
              ]

    return topics
