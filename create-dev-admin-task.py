#!/usr/bin/env python

import getopt
import os
import sys

from lib.tasks import DevTaskType
from lib.tasks import DevWorkType
from lib.ui import ui_create_root_dev_admin_task
from lib.ui import ui_create_subtasks
from lib.ui import ui_create_subtasks_from_file
from lib.ui import ui_select_project
from todoist_api_python.api import TodoistAPI

import questionary
from rich.console import Console

console = Console()

def main(subtasks_path, work_type):
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)

    (project_id, _) = ui_select_project(api, work_type)
    root_task_id = ui_create_root_dev_admin_task(api, project_id, work_type)
    if subtasks_path:
        ui_create_subtasks_from_file(
            api, subtasks_path, project_id, root_task_id, DevTaskType.ADMIN, work_type)
    else:
        create_subtasks = questionary.confirm('Would you like to create any subtasks').ask()
        if create_subtasks:
            ui_create_subtasks(
                api,
                root_task_id,
                project_id,
                DevTaskType.ADMIN,
                work_type)

if __name__ == '__main__':
    work_type = DevWorkType.WORK
    subtasks_path = ""
    opts, args = getopt.getopt(sys.argv[1:], "", ["personal", "subtasks-path="])
    for opt, arg in opts:
        if opt in "--personal":
            work_type = DevWorkType.PERSONAL
        elif opt in "--subtasks-path":
            subtasks_path = arg
    sys.exit(main(subtasks_path, work_type))
