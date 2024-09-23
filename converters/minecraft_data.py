import json


class MinecraftData:
    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return json_dict


def extract_items_and_blocks(mcdata: MinecraftData) -> tuple[list, list]:
    """Extract Items And Blocks From Minecraft Data."""
    mcitems = [
        item.replace("minecraft.", "")
        for item in mcdata[0]["language"]["item"]
        if item.startswith("minecraft.")
    ]
    mcblocks = [
        item.replace("minecraft.", "")
        for item in mcdata[0]["language"]["block"]
        if item.startswith("minecraft.")
    ]
    return mcitems, mcblocks
