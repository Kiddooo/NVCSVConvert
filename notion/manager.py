import requests


class NotionManager:
    def __init__(
        self, notion_api: str, notion_secret: str, notion_version: str, console=None
    ):
        self.console = console
        self.url = notion_api
        self.headers = {
            "Authorization": f"Bearer {notion_secret}",
            "Notion-Version": notion_version,
            "Content-Type": "application/json",
        }

    def query_notion_database(self):
        try:
            self.console.clear()
            with self.console.status("[bold yellow]Querying Notion database..."):
                response = requests.post(self.url, headers=self.headers, timeout=30)
                response.raise_for_status()

            self.console.print(
                "[bold yellow]✓[/bold yellow] Successfully retrieved data from Notion"
            )
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            self.console.print(f"[bold red]HTTP Error:[/bold red] {http_err}")
            self.console.print("[bold yellow]Response Content:[/bold yellow]")
            try:
                self.console.print_json(response.text)
            except:
                self.console.print(response.text)

        except requests.exceptions.RequestException as req_err:
            self.console.print(f"[bold red]Request Error:[/bold red] {req_err}")

        except json.JSONDecodeError as json_err:
            self.console.print(f"[bold red]JSON Parsing Error:[/bold red] {json_err}")
            self.console.print("[bold yellow]Response Content:[/bold yellow]")
            self.console.print(response.text)

        except:
            self.console.print_exception()

        return None
