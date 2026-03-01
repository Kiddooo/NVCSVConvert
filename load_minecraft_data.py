import json


class MinecraftData:
    def __init__(self, version: str, console=None) -> None:
        self.version = version
        self.console = console

    def from_json(self, json_str: str) -> dict:
        try:
            json_dict = json.loads(json_str)
            if not isinstance(json_dict, dict):
                raise ValueError("Expected JSON array as input")
            return json_dict
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def load_data(self, file_path: str, extractor=None) -> dict:
        try:
            return self.read_minecraft_data(file_path, extractor=extractor)
        except FileNotFoundError:
            self.console.print(f"[red]File not found: {file_path}[/red]")
            self.console.print(f"[yellow]Attempting to extract data...[/yellow]")

            extractor.extract_data(minecraft_data=self)

            return self.read_minecraft_data(f"{self.version}.json", extractor=extractor)

    def read_minecraft_data(self, file_path: str, extractor=None) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as version_file:
                return self.from_json(version_file.read())
        except FileNotFoundError:
            extractor.extract_data(minecraft_data=self)
            return self.read_minecraft_data(f"{self.version}.json", extractor=extractor)
