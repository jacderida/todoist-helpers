#!/usr/bin/env python

import getopt
import os
import sys

from dev.tasks import DevTaskType
from dev.tasks import DevWorkType
from dev.tasks import create_jira_admin_task
from dev.tasks import create_subtask
from dev.ui import ui_create_root_dev_task
from dev.ui import ui_get_jira_or_branch_ref
from projects import get_project_id
from todoist.api import TodoistAPI

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def main(subtasks_path, task_type, work_type):
    project_id = get_project_id(api, "General/Ad-hoc")
    jira_ref = ui_get_jira_or_branch_ref()
    root_task_id = ui_create_root_dev_task(
        api, project_id, jira_ref, task_type, work_type, extra_labels=["support"])
    create_subtask(api, "Investigate or reproduce the issue", project_id, task_type, work_type, root_task_id)
    create_subtask(api, "Determine the cause of the issue", project_id, task_type, work_type, root_task_id)
    create_subtask(api, "Fix the issue or create new task", project_id, task_type, work_type, root_task_id)
    if os.getenv('JIRA_BASE_URL'):
        create_jira_admin_task(api, project_id, root_task_id, jira_ref)

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
