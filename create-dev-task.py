#!/usr/bin/env python

import getopt
import os
import sys

from lib.tasks import DevTaskType
from lib.tasks import DevWorkType
from lib.tasks import create_jira_admin_task
from lib.tasks import create_merge_subtasks
from lib.tasks import create_pr_checklist_subtask
from lib.ui import ui_create_root_dev_task
from lib.ui import ui_create_subtasks
from lib.ui import ui_create_subtasks_from_file
from lib.ui import ui_get_jira_or_branch_ref
from lib.ui import ui_select_project
from lib.ui import ui_select_repository

import questionary
from rich.console import Console
from todoist_api_python.api import TodoistAPI

console = Console()

def main(subtasks_path, task_type, work_type):
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)
    (project_id, _) = ui_select_project(api, work_type)
    branch_ref = ""
    repo = ""
    if task_type != DevTaskType.NON_CODE:
        branch_ref = ui_get_jira_or_branch_ref()
    if task_type != DevTaskType.NON_CODE:
        (_, repo, _) = ui_select_repository("Select Repository for Work")
    root_task_id = ui_create_root_dev_task(api, project_id, branch_ref, task_type, work_type, repo)
    if subtasks_path:
        ui_create_subtasks_from_file(
            api, subtasks_path, root_task_id, project_id, task_type, work_type)
    else:
        create_subtasks = questionary.confirm("Would you like to create any subtasks").ask()
        if create_subtasks:
            ui_create_subtasks(
                api,
                root_task_id,
                project_id,
                task_type,
                work_type)
    if task_type != DevTaskType.NON_CODE:
        create_pr_checklist_subtask(api, project_id, root_task_id, branch_ref, task_type, work_type)
        create_merge_subtasks(
            api, project_id, root_task_id, branch_ref, repo, 'main', task_type, work_type)
    if os.getenv("JIRA_BASE_URL"):
        create_jira_admin_task(api, project_id, root_task_id, branch_ref)

if __name__ == "__main__":
    task_type = DevTaskType.RUST
    work_type = DevWorkType.WORK
    subtasks_path = ""
    opts, args = getopt.getopt(sys.argv[1:], "", ["personal", "subtasks-path=", "task-type="])
    for opt, arg in opts:
        if opt in "--personal":
            work_type = DevWorkType.PERSONAL
        elif opt in "--subtasks-path":
            subtasks_path = arg
        elif opt in "--task-type":
            task_type = DevTaskType[arg]
    sys.exit(main(subtasks_path, task_type, work_type))
