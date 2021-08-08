#!/usr/bin/env python

import getopt
import os
import sys

from dev.tasks import DevTaskType
from dev.tasks import DevWorkType
from dev.tasks import create_jira_admin_task
from dev.tasks import create_merge_subtask
from dev.ui import ui_create_root_dev_task
from dev.ui import ui_create_subtasks
from dev.ui import ui_create_subtasks_from_file
from dev.ui import ui_get_jira_or_branch_ref
from dev.ui import ui_get_main_repo
from dev.ui import ui_select_project
from todoist.api import TodoistAPI

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def main(subtasks_path, task_type, work_type):
    project_id = ui_select_project(api, work_type)[1]
    branch_ref = ui_get_jira_or_branch_ref()
    repos = ui_get_main_repo(work_type)
    root_task_id = ui_create_root_dev_task(api, project_id, branch_ref, task_type, work_type, repos)
    if subtasks_path:
        ui_create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type)
    else:
        ui_create_subtasks(
            api,
            root_task_id,
            project_id,
            "Define Subtasks for Work",
            "Create any subtasks for this work",
            task_type,
            work_type)
    for repo in repos:
        create_merge_subtask(api, project_id, root_task_id, branch_ref, repo, "master", task_type, work_type)
    if os.getenv('JIRA_BASE_URL'):
        create_jira_admin_task(api, project_id, root_task_id, branch_ref)

if __name__ == '__main__':
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
