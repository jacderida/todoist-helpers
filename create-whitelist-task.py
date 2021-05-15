#!/usr/bin/env python

import os
import sys

from todoist.api import TodoistAPI

from dev.tasks import create_jira_admin_task
from dev.tasks import create_branch_subtask
from dev.tasks import create_merge_subtask
from dev.tasks import create_parent_task
from dev.tasks import create_subtask
from dev.tasks import create_terraform_merge_subtask
from dev.ui import print_heading
from dev.ui import ui_create_root_task
from dev.ui import ui_create_subtasks
from dev.ui import ui_get_jira_reference
from dev.ui import ui_get_whitelist_entries_to_create
from labels import get_label_ids
from projects import get_project_id
from projects import ui_select_work_project

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def create_main_repo_subtasks(project_id, root_task_id, jira_ref, modules):
    for module in modules.keys():
        create_subtask(
            api,
            "Update `terraform` to use `{version}` of `{module}`".format(
                version=modules[module], module=module),
            project_id,
            root_task_id)

def main():
    project_id = get_project_id(api, "DCF: General")
    jira_ref = ui_get_jira_reference()
    whitelist_entries = ui_get_whitelist_entries_to_create()
    content = "[{jira_ref}]({jira_link}/{jira_ref}): ".format(
        jira_ref=jira_ref,
        jira_link=os.environ["JIRA_BASE_URL"])
    if len(whitelist_entries) > 1:
        content += "Whitelist New IP Addresses for `int`"
    else:
        content += "Whitelist {} for {} on `int`".format(
            whitelist_entries[0][1], whitelist_entries[0][0])
    parent_task = create_parent_task(api, content, project_id)
    if len(whitelist_entries) > 1:
        for entry in whitelist_entries:
            create_subtask(
                api,
                "Whitelist IP {} for {}".format(entry[1], entry[0]),
                project_id,
                parent_task["id"])
    create_terraform_merge_subtask(api, project_id, parent_task["id"], jira_ref, "master")
    for entry in whitelist_entries:
        create_subtask(
            api,
            "Verify access for {}".format(entry[0]),
            project_id,
            parent_task["id"])
    create_jira_admin_task(api, project_id, parent_task["id"], jira_ref)

if __name__ == '__main__':
    sys.exit(main())
