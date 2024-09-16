class ShopItem:
    def __init__(self, shop_row):
        self._shop_name = shop_row["Shop Name"]["title"][0]["plain_text"]
        self._inventory = shop_row["Inventory"]["rich_text"][0]["plain_text"].split(
            ", "
        )
        try:
            self._coords = shop_row["Coords (X, Z)"]["rich_text"][0]["plain_text"]
        except IndexError:
            self._coords = ""
        self._owner_ign = shop_row["Owner IGN"]["rich_text"][0]["plain_text"]
        try:
            self._spawn = shop_row["Spawn"]["select"]["name"]
        except Exception as e:
            print(shop_row, e)

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
