import csv
import topics
import items


class CharacterProfile:
    """The container for all of the player's stats, progress and inventory."""
    def __init__(self):
        # Lists of various collections
        self.topics = topics.init_topics("scenes/topics.csv")
        self.inventory = Inventory()


class Inventory:
    """A container for item objects the player has accumulated."""
    def __init__(self):
        self.bag = self._init_items()

    def _init_items(self):
        """Creates a full list of all items in the game. Items are initialized with no stock,
        meaning they do not appear in any invetory screen until stock is added.
        This becomes the player's bag going forward."""
        bag = {}

        with open("scenes/items.csv", newline='') as itemsfile:
            items_csv_reader = csv.reader(itemsfile)
            for each_line in items_csv_reader:

                # Check if the item has_stock is enabled
                if "has_stock" in each_line[3]:
                    has_stock = True
                else:
                    has_stock = False

                bag[each_line[0]] = items.Item(each_line[0], each_line[1], each_line[2], has_stock)

        return bag

    def add(self, item_name, quantity=1):
        """Adds the given item in the given quantity to the bag.
        If the item cannot stock, then it simply adds one."""
        # Given a negative quantity, default to the remove() function
        if quantity < 0:
            self.remove(item_name, quantity * -1)

        if item_name in self.bag.keys():
            # Check if the item has a stock of None, meaning it has not been picked up
            if self.bag[item_name].stock is None:
                if self.bag[item_name].can_stock:
                    self.bag[item_name].stock = quantity
                else:
                    self.bag[item_name].stock = 1

            else:
                if self.bag[item_name].can_stock:
                    self.bag[item_name].stock += quantity
                else:
                    self.bag[item_name].stock = 1

    def remove(self, item_name, quantity=1):
        """Removes the given item in the given quantity from the inventory. If quantity='all' then it will completely
        remove the item."""

        if self.bag[item_name].stock is not None:

            # Check for 'all'
            if quantity == "all":
                self.bag[item_name].stock = None
            else:
                self.bag[item_name].stock -= quantity
                if self.bag[item_name].stock <= 0:
                    self.bag[item_name].stock = None
