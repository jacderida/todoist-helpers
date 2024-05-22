#!/usr/bin/env python

import getopt
import os
import sys

from lib.tasks import TaskType
from lib.tasks import WorkType
from lib.tasks import create_jira_admin_task
from lib.tasks import create_subtask
from lib.tasks import create_subtasks_from_file
from lib.ui import ui_create_root_dev_bug_investigation_task
from lib.ui import ui_select_project
from todoist_api_python.api import TodoistAPI

def main(subtasks_path, task_type, work_type):
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)

    project_id = ui_select_project(api, work_type)[0]
    root_task_id = ui_create_root_dev_bug_investigation_task(
        api, project_id, work_type, extra_labels=["bug/issue"])
    if subtasks_path:
        create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type)
    else:
        create_subtask(api, "Reproduce the issue", project_id, task_type, work_type, root_task_id)
        create_subtask(api, "Determine the cause of the issue", project_id, task_type, work_type, root_task_id)
        create_subtask(api, "Create new task for fix", project_id, task_type, work_type, root_task_id)
    if os.getenv('JIRA_BASE_URL'):
        create_jira_admin_task(api, project_id, root_task_id, None)

if __name__ == "__main__":
    no_branch = False;
    task_type = TaskType.DEV
    work_type = WorkType.WORK
    subtasks_path = ""
    project_name = ""
    opts, args = getopt.getopt(sys.argv[1:], "", ["personal", "subtasks-path=", "task-type="])
    for opt, arg in opts:
        if opt in "--personal":
            work_type = WorkType.PERSONAL
        elif opt in "--subtasks-path":
            subtasks_path = arg
        elif opt in "--task-type":
            task_type = TaskType[arg]
    sys.exit(main(subtasks_path, task_type, work_type))
