class ShopItem:
    def __init__(self, shop_row):
        self._shop_name = shop_row[0]
        self._inventory = shop_row[1].split(",")
        self._coords = shop_row[2]
        self._owner_ign = shop_row[3]
        self._spawn = shop_row[4]

    def get_shop_name(self) -> str:
        return self._shop_name

    def get_inventory(self) -> list:
        return list(self._inventory)

    def get_coords(self) -> str:
        return self._coords

    def get_owner_ign(self) -> str:
        return self._owner_ign

    def get_spawn(self) -> str:
        return self._spawn
