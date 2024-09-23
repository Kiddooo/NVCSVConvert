import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def query_notion_database():
    # Set up the API endpoint URL
    url = f'{os.getenv("NOTION_API")}'

    # Define the headers required for the Notion API
    headers = {
        "Authorization": f'Bearer {os.getenv("NOTION_SECRET")}',
        "Notion-Version": os.getenv("NOTION_VERSION"),
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = json.loads(response.text)

            return result
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
