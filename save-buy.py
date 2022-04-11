#!/usr/bin/env python

import os
import sys

import questionary
from rich.console import Console
from todoist.api import TodoistAPI

from lib.tasks import create_task

BUY_PROJECT_ID = 2228704164

console = Console()


def create_item_to_buy(api, content, labels, link, notes):
    task = create_task(
        api,
        content,
        BUY_PROJECT_ID,
        None,
        None,
        None,
        labels,
        link,
        False,
    )
    if notes:
        api.notes.add(task["id"], notes)
        api.commit()


def main():
    api_token = os.getenv("TODOIST_API_TOKEN")
    with console.status("[bold green]Initial Todoist API sync...") as _:
        api = TodoistAPI(api_token)
        api.sync()
    link = questionary.text("Link?").ask()
    item_type = questionary.select("Type?", choices=["book", "film"]).ask()
    if item_type == "book":
        author = questionary.text("Author?").ask()
        title = questionary.text("Title?").ask()
        amount = questionary.text("Price?").ask()
        notes = questionary.text("Notes?").ask()
        content = f"{author} - '{title}'"
        if amount:
            content += f" (£{amount})"
        create_item_to_buy(api, content, ["buy", "books"], link, notes)
    elif item_type == "film":
        title = questionary.text("Title?").ask()
        media_type = questionary.select("Type?", choices=["Blu-ray", "DVD"]).ask()
        year = questionary.text("Year?").ask()
        notes = questionary.text("Notes?").ask()
        create_item_to_buy(
            api, f"'{title}' ({media_type}, {year})", ["buy", "films"], link, notes
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
