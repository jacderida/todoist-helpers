#!/usr/bin/env python

import os
import sys

from dev.tasks import create_jira_admin_task
from dev.tasks import create_merge_subtask
from dev.tasks import create_subtask
from dev.tasks import create_terraform_merge_subtask
from dev.ui import ui_create_root_task
from dev.ui import ui_create_sub_tasks
from dev.ui import ui_get_jira_reference

from todoist.api import TodoistAPI
from labels import get_label_ids
from projects import ui_get_user_project_selection

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def ui_get_terraform_modules():
    modules = [
        "terraform_dcf_entrypoint",
        "terraform_dcf_networking"
    ]
    print("The following modules are available:")
    count = 1
    for module in modules:
        print("{num}. {name}".format(num=count, name=module))
        count += 1
    print("Use a comma separated list to select the modules to modify (enter 'none' if you don't need any for this task)")
    selected = input(">> ")
    if selected == "none":
        return {}
    print()

    selected_modules = [modules[int(x) - 1] for x in selected.split(",")]
    print("Please provide the new version number for each module...")
    module_version_map = {}
    for selected_module in selected_modules:
        version = input("{name}: ".format(name=selected_module))
        module_version_map[selected_module] = version
    print()
    return module_version_map

def create_module_subtasks(project_id, root_task_id, jira_ref, modules):
    for module in modules.keys():
        create_merge_subtask(api, project_id, root_task_id, jira_ref, module, "master")
        create_subtask(
            api,
            "Tag `{module}` at `{version}`".format(module=module, version=modules[module]),
            project_id,
            root_task_id)

def create_main_repo_subtasks(project_id, root_task_id, jira_ref, modules):
    for module in modules.keys():
        create_subtask(
            api,
            "Update `terraform` to use `{version}` of `{module}`".format(
                version=modules[module], module=module),
            project_id,
            root_task_id)
    create_terraform_merge_subtask(api, project_id, root_task_id, jira_ref, "master")

def main():
    project_id = ui_get_user_project_selection(api)[1]
    jira_ref = ui_get_jira_reference()
    root_id = ui_create_root_task(api, project_id, jira_ref)
    ui_create_sub_tasks(api, root_id, project_id)
    modules = ui_get_terraform_modules()
    create_module_subtasks(project_id, root_id, jira_ref, modules)
    create_main_repo_subtasks(project_id, root_id, jira_ref, modules)
    create_jira_admin_task(api, project_id, root_id, jira_ref)

if __name__ == '__main__':
    sys.exit(main())
