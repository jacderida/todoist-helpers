#!/usr/bin/env python

import os
import sys

from todoist.api import TodoistAPI
from labels import get_label_ids
from lib import create_merge_subtask
from lib import create_subtask
from lib import create_terraform_merge_subtask
from projects import get_user_project_selection

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def get_jira_reference():
    print("Please supply the JIRA reference")
    jira_ref = input(">> ")
    return jira_ref

def create_root_task(project_id, jira_ref):
    print("Please supply the name of the main task")
    name = input(">> ")
    print("Creating task '{name} [{jira_ref}]'".format(name=name, jira_ref=jira_ref))
    root_task = api.items.add(
        "{name} [{jira_ref}]".format(name=name, jira_ref=jira_ref),
        project_id=project_id,
        labels=get_label_ids(api, ["work", "development"]))
    api.commit()
    return root_task['id']

def create_sub_tasks(root_task_id, project_id):
    while True:
        print("Please enter the name of a subtask to add (or enter 'quit' to stop)")
        name = input(">> ")
        if name == "quit":
            break
        create_subtask(api, name, project_id, root_task_id)

def get_terraform_modules():
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
    project_id = get_user_project_selection(api)[1]
    jira_ref = get_jira_reference()
    root_id = create_root_task(project_id, jira_ref)
    create_sub_tasks(root_id, project_id)
    modules = get_terraform_modules()
    create_module_subtasks(project_id, root_id, jira_ref, modules)
    create_main_repo_subtasks(project_id, root_id, jira_ref, modules)

if __name__ == '__main__':
    sys.exit(main())
