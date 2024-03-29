#!/usr/bin/env python

import os
import sys

import questionary
from rich.console import Console
from todoist_api_python.api import TodoistAPI

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
        api.add_comment(task_id=task["id"], content=notes)


def main():
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)
    link = questionary.text("Link?").ask()
    item_type = questionary.select("Type?", choices=["book", "film"]).ask()
    if item_type == "book":
        author = questionary.text("Author?").ask()
        title = questionary.text("Title?").ask()
        notes = questionary.text("Notes?").ask()
        create_item_to_buy(api, f"{author} - '{title}'", ["buy", "books"], link, notes)
    elif item_type == "film":
        title = questionary.text("Title?").ask()
        media_type = questionary.select(
            "Type?", choices=["Blu-ray", "Digital", "DVD"]
        ).ask()
        if media_type == "Blu-ray":
            sub_type = questionary.select(
                "Blu-ray type?", choices=["1080p", "4k"]
            ).ask()
            media_type += f" {sub_type}"
        notes = questionary.text("Notes?").ask()
        create_item_to_buy(
            api, f"'{title}' ({media_type})", ["buy", "films"], link, notes
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
