import topics


class CharacterProfile:
    """The container for all of the player's stats, progress and inventory."""
    def __init__(self):
        # Lists of various collections
        self.topics = topics.init_topics()
