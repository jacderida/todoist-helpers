#!/usr/bin/env python

import os
import sys

from dev.tasks import create_jira_admin_task
from dev.tasks import create_merge_subtask
from dev.tasks import create_subtask
from dev.tasks import create_subtasks_from_file
from dev.ui import ui_create_root_task
from dev.ui import ui_create_subtasks
from dev.ui import ui_create_subtasks_from_file
from dev.ui import ui_get_jira_reference
from dev.ui import ui_get_main_repo
from projects import ui_get_user_project_selection
from todoist.api import TodoistAPI

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def main(subtasks_path):
    project_id = ui_get_user_project_selection(api)[1]
    jira_ref = ui_get_jira_reference()
    main_repo = ui_get_main_repo()
    root_task_id = ui_create_root_task(api, project_id, jira_ref, main_repo)
    if subtasks_path:
        ui_create_subtasks_from_file(api, subtasks_path, project_id, root_task_id)
    else:
        ui_create_subtasks(
            api,
            root_task_id,
            project_id,
            "Define Subtasks for Work",
            "Create any subtasks for this work")
    create_merge_subtask(api, project_id, root_task_id, jira_ref, main_repo, "master")
    create_jira_admin_task(api, project_id, root_task_id, jira_ref)

if __name__ == '__main__':
    subtasks_path = ""
    if len(sys.argv) >= 2:
        subtasks_path = sys.argv[1]
    sys.exit(main(subtasks_path))
