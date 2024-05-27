#!/usr/bin/env python

import getopt
import os
import sys

from lib.tasks import create_task, TaskType, WorkType
from todoist_api_python.api import TodoistAPI

import questionary
from rich.console import Console

ARCHIVE_PROJECT_ID = 2288914343
TAPE_LOCATE_SECTION_ID = 156613680

console = Console()

def main(tasks_path):
    work_type = WorkType.PERSONAL
    task_type = TaskType.RESEARCH

    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)

    if tasks_path:
        with open(tasks_path, "r") as f:
            for line in f.readlines():
                name = line.strip()
                create_task(
                    api,
                    f"Attempt to locate the `{name}` tape in the 911datasets.org releases",
                    ARCHIVE_PROJECT_ID,
                    task_type,
                    work_type,
                    apply_date=False,
                    section_id=TAPE_LOCATE_SECTION_ID)
    else:
        name = questionary.text(
            "Provide the tape name:",
            validate=lambda answer: True if len(answer) > 0 else "A name for the tape must be provided"
        ).ask()
        create_task(
            api,
            f"Attempt to locate the `{name}` tape in the 911datasets.org releases",
            ARCHIVE_PROJECT_ID,
            task_type,
            work_type,
            apply_date=True,
            section_id=TAPE_LOCATE_SECTION_ID)

if __name__ == '__main__':
    tasks_path = None
    opts, args = getopt.getopt(sys.argv[1:], "", ["tasks-path="])
    for opt, arg in opts:
        if opt in "--tasks-path":
            tasks_path = arg
    sys.exit(main(tasks_path))
