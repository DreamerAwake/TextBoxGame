class Item:
    def __init__(self, name, item_category, description, can_stock=False):
        """Base class for items."""
        self.name = name
        self.description = description
        self.type = item_category

        self.can_stock = can_stock
        self.stock = None
