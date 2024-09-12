import json


class MinecraftData:
    @classmethod
    def from_json(cls, json_str):
        json_dict = json.loads(json_str)
        return json_dict
