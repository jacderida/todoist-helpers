#!/usr/bin/env python

import getopt
import os
import sys

from dev.tasks import DevTaskType
from dev.tasks import DevWorkType
from dev.tasks import create_jira_admin_task
from dev.tasks import create_subtask
from dev.tasks import create_subtasks_from_file
from dev.ui import ui_create_root_dev_task
from dev.ui import ui_get_jira_or_branch_ref
from dev.ui import ui_select_project
from todoist.api import TodoistAPI
from projects import get_project_id

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def main(subtasks_path, task_type, work_type, no_branch, project_name):
    project_id = ""
    if project_name:
        project_id = get_project_id(api, project_name);
    else:
        project_id = ui_select_project(api, work_type)[1]
    branch_ref = ""
    if not no_branch:
        branch_ref = ui_get_jira_or_branch_ref()
    root_task_id = ui_create_root_dev_task(
        api, project_id, branch_ref, task_type, work_type, extra_labels=["bug/issue"])
    if subtasks_path:
        create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type)
    else:
        create_subtask(api, "Investigate or reproduce the issue", project_id, task_type, work_type, root_task_id)
        create_subtask(api, "Determine the cause of the issue", project_id, task_type, work_type, root_task_id)
        create_subtask(api, "Fix the issue or create new task", project_id, task_type, work_type, root_task_id)
    if os.getenv('JIRA_BASE_URL'):
        create_jira_admin_task(api, project_id, root_task_id, branch_ref)

if __name__ == "__main__":
    no_branch = False;
    task_type = DevTaskType.RUST
    work_type = DevWorkType.WORK
    subtasks_path = ""
    project_name = ""
    opts, args = getopt.getopt(sys.argv[1:], "", ["personal", "subtasks-path=", "task-type=", "nobranch", "project-name="])
    for opt, arg in opts:
        if opt in "--personal":
            work_type = DevWorkType.PERSONAL
        elif opt in "--subtasks-path":
            subtasks_path = arg
        elif opt in "--task-type":
            task_type = DevTaskType[arg]
        elif opt in "--nobranch":
            no_branch = True
        elif opt in "--project-name":
            project_name = arg
    sys.exit(main(subtasks_path, task_type, work_type, no_branch, project_name))
