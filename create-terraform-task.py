#!/usr/bin/env python

import os
import sys

from dev.tasks import create_jira_admin_task
from dev.tasks import create_branch_subtask
from dev.tasks import create_merge_subtask
from dev.tasks import create_subtask
from dev.tasks import create_terraform_merge_subtask
from dev.ui import print_heading
from dev.ui import ui_create_root_task
from dev.ui import ui_create_subtasks
from dev.ui import ui_get_jira_reference

from todoist.api import TodoistAPI
from labels import get_label_ids
from projects import ui_get_user_project_selection

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def ui_get_terraform_modules():
    print_heading("Module Selection")
    modules = [
        "terraform_cms_dns",
        "terraform_dcf_entrypoint",
        "terraform_dcf_networking"
    ]
    print("The following modules are available to work with:")
    count = 1
    for module in modules:
        print("{num}. {name}".format(num=count, name=module))
        count += 1
    print("Select a module or use a comma separated list to select multiple")
    print("Enter 'none' if you don't need to modify any modules for this work")
    selected = input(">> ")
    if selected == "none":
        return {}
    print()

    if "," in selected:
        selected_modules = [modules[int(x) - 1] for x in selected.split(",")]
    else:
        selected_modules = [modules[int(selected) - 1]]
    print_heading("Module Versions")
    print("Please provide the new version number for each selected module")
    module_version_map = {}
    for selected_module in selected_modules:
        version = input("{name}: ".format(name=selected_module))
        module_version_map[selected_module] = version
    return module_version_map

def create_module_subtasks(project_id, root_task_id, jira_ref, modules):
    for module in modules.keys():
        create_branch_subtask(api, project_id, root_task_id, jira_ref, module)
        print()
        ui_create_subtasks(
            api,
            root_task_id,
            project_id,
            "{module} subtasks".format(module=module),
            "Create any subtasks for the {module} module".format(module=module))
        create_merge_subtask(api, project_id, root_task_id, jira_ref, module, "master")
        create_subtask(
            api,
            "Tag `{module}` at `{version}`".format(module=module, version=modules[module]),
            project_id,
            root_task_id)
    print()

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
    root_id = ui_create_root_task(api, project_id, jira_ref, "terraform")
    ui_create_subtasks(
        api,
        root_id,
        project_id,
        "Define Main Repo Subtasks",
        "Create any subtasks for main terraform repo")
    modules = ui_get_terraform_modules()
    create_module_subtasks(project_id, root_id, jira_ref, modules)
    create_main_repo_subtasks(project_id, root_id, jira_ref, modules)
    create_jira_admin_task(api, project_id, root_id, jira_ref)
    ui_create_subtasks(
        api,
        root_id,
        project_id,
        "Define Post-Merge Subtasks",
        "Create any subtasks to be performed after merging")

if __name__ == '__main__':
    sys.exit(main())
