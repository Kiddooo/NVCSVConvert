import json
from pathlib import Path
from typing import List, Tuple

import requests


class MinecraftExtractor:
    def __init__(
        self,
        version: str,
        output_file_path: str,
        toppings: str = "items,blocks",
        console=None,
    ) -> None:
        self.version = version
        self.output_file_path = output_file_path
        self.toppings = toppings
        self.console = console

    def extract_version_data(self) -> None:
        self.console.print(f"Downloading data for version {self.version}...")
        try:
            version_request_data = requests.get(
                f"https://raw.githubusercontent.com/Pokechu22/Burger/gh-pages/{self.version}.json"
            ).json()[0]["language"]

            processed_data = {
                "blocks": {
                    key.replace("minecraft.", ""): value
                    for key, value in version_request_data["block"].items()
                    if key.startswith("minecraft.")
                },
                "items": {
                    key.replace("minecraft.", ""): value
                    for key, value in version_request_data["item"].items()
                    if key.startswith("minecraft.")
                },
            }

            with open(self.output_file_path, "w", encoding="utf-8") as output_file:
                json.dump(processed_data, output_file, indent=4)
            self.console.print(
                f"Data for version {self.version} downloaded successfully."
            )

        except Exception as e:
            self.console.print(
                f"Error downloading data for version {self.version}: {str(e)}"
            )
            return

    def extract_data(self, minecraft_data=None) -> Tuple[List[str], List[str]]:
        if not Path(self.output_file_path).exists():
            self.extract_version_data()
        minecraft_data = minecraft_data.load_data(file_path=self.output_file_path)
        return list(minecraft_data["items"]), list(minecraft_data["blocks"])
