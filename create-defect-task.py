#!/usr/bin/env python

import os
import sys

from dev.tasks import create_jira_admin_task
from dev.tasks import create_subtask
from dev.ui import ui_create_root_task
from dev.ui import ui_get_jira_reference
from projects import get_project_id
from projects import ui_select_work_project
from todoist.api import TodoistAPI

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def main(subtasks_path):
    project_id = ui_select_work_project(api)[1]
    jira_ref = ui_get_jira_reference()
    root_task_id = ui_create_root_task(api, project_id, jira_ref, extra_labels=["bug/issue"])
    create_subtask(api, "Investigate or reproduce the issue", project_id, root_task_id)
    create_subtask(api, "Determine the cause of the issue", project_id, root_task_id)
    create_subtask(api, "Fix the issue or create new task", project_id, root_task_id)
    create_jira_admin_task(api, project_id, root_task_id, jira_ref)

if __name__ == '__main__':
    subtasks_path = ""
    if len(sys.argv) >= 2:
        subtasks_path = sys.argv[1]
    sys.exit(main(subtasks_path))
