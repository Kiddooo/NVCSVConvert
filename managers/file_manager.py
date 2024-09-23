import csv
import logging
import os
import subprocess
from typing import List

from constants import VERSION
from converters.minecraft_data import MinecraftData


def save_to_csv(filename: str, data: List[str]):
    """Save Data To CSV File."""
    with open(file=filename, mode="a", encoding="utf8", newline="") as csvfile_writer:
        writer = csv.writer(
            csvfile_writer, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(data)


def load_minecraft_data(file_path: str) -> MinecraftData:
    """Load Minecraft Data From A JSON File."""
    try:
        with open(file_path, "r", encoding="utf8") as version_file:
            return MinecraftData().from_json(version_file.read())
    except FileNotFoundError:
        extract_version_data(
            version=VERSION, output_file=f"{VERSION}.json", toppings="items,blocks"
        )
        # Wait for the subprocess to finish
        subprocess.run(["python", "-m", "subprocess"], capture_output=True, text=True)

        # Try to load the newly created file
        try:
            with open(f"{VERSION}.json", "r", encoding="utf8") as version_file:
                return MinecraftData().from_json(version_file.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"Failed to create {VERSION}.json file")


def extract_version_data(version: str, output_file: str, toppings: str):
    """Extract block and item information using Burger"""
    logging.info(
        f"Downloading version {version}'s block and item information, Please wait..."
    )
    subprocess.run(
        [
            "python",
            "Burger/munch.py",
            "-d",
            version,
            "--output",
            output_file,
            "--toppings",
            toppings,
        ]
    )
    os.remove(version + ".jar")
