import os
from pathlib import Path

from .tasks import DevTaskType
from .tasks import DevWorkType
from .tasks import create_parent_task
from .tasks import create_subtask
from .tasks import create_subtasks_from_file
from .tasks import create_branch_subtask

import questionary
from questionary import Validator, ValidationError
from rich.console import Console

console = Console()

DEV_DIR_NAME = 'dev'
PERSONAL_PARENT_PROJECT_ID = 2181705102
WORK_PARENT_PROJECT_ID = 2235604758

class JiraBranchRefValidator(Validator):
    def validate(self, document):
        if ' ' in document.text:
            raise ValidationError(
                message='The JIRA/branch reference cannot contain spaces',
                cursor_position=len(document.text)
            )
        if any([c.isupper() for c in document.text]):
            raise ValidationError(
                message='The JIRA/branch reference must be all lower case',
                cursor_position=len(document.text)
            )
        if len(document.text) == 0:
            raise ValidationError(
                message='A value must be provided for the JIRA/branch reference',
                cursor_position=len(document.text)
            )


def ui_select_repository(header_text):
    print_heading(header_text)
    dev_path = Path.home().joinpath(DEV_DIR_NAME)
    sites = sorted(os.listdir(dev_path))
    site = questionary.select('Please select the site', choices=sites).ask()
    site_path = dev_path.joinpath(site)
    owners = sorted(os.listdir(site_path))
    owner = questionary.select('Please select the owner', choices=owners).ask()
    owner_path = site_path.joinpath(owner)
    repositories = sorted(os.listdir(owner_path))
    repo = questionary.select('Please select the repository', choices=repositories).ask()
    return (owner, repo, owner_path.joinpath(repo))


def ui_get_jira_or_branch_ref():
    jira_ref = questionary.text(
        'Please supply the JIRA or branch reference:', validate=JiraBranchRefValidator
    ).ask()
    return jira_ref


def ui_create_subtasks(api, root_task_id, project_id, task_type, work_type):
    while True:
        name = questionary.text(
            "Please enter the name of the subtask to add (or use 'quit' to stop):",
            validate=lambda name: True if len(name) > 0 else 'The subtask must have a name'
        ).ask()
        if name == 'quit':
            break
        create_subtask(api, name, project_id, task_type, work_type, root_task_id)
    print()


def ui_create_root_dev_task(
        api, project_id, branch_ref, task_type, work_type, repo='', extra_labels=[]):
    name = questionary.text(
        'Provide a name for the development task:',
        validate=lambda answer: True if len(answer) > 0 else 'A name for the task must be provided'
    ).ask()
    task_name = name
    jira_url = os.getenv('JIRA_BASE_URL')
    if jira_url:
        task_name = f'[{branch_ref}]({jira_url}/{branch_ref}): {name}'
    root_task = create_parent_task(
        api, task_name, project_id, task_type, work_type, extra_labels=extra_labels)
    root_task_id = root_task["id"]
    if repo:
        create_branch_subtask(api, project_id, root_task_id, task_name, work_type, repo, branch_ref)
    print()
    return root_task_id


def ui_create_root_dev_admin_task(api, project_id, work_type, extra_labels=[]):
    task_name = questionary.text(
        'Provide a name for the development task:',
        validate=lambda answer: True if len(answer) > 0 else 'A name for the task must be provided'
    ).ask()
    root_task = create_parent_task(
        api, task_name, project_id, DevTaskType.ADMIN, work_type, extra_labels=extra_labels)
    root_task_id = root_task['id']
    return root_task_id


def ui_create_root_dev_investigation_task(api, project_id, work_type, extra_labels=[]):
    task_name = questionary.text(
        'Provide a name for the investigation to carry out:',
        validate=lambda answer: True if len(answer) > 0 else 'A name for the task must be provided'
    ).ask()
    root_task = create_parent_task(
        api, task_name, project_id, DevTaskType.INVESTIGATION, work_type, extra_labels=extra_labels)
    root_task_id = root_task['id']
    print()
    return root_task_id


def ui_get_whitelist_entries_to_create():
    whitelist_entries = []
    print_heading("Create New Whitelist Task")
    while True:
        print("Please enter the name and IP address of the person for whitelisting.")
        print("They should be separated by a semi-colon.")
        print("Enter 'quit' to stop adding entries")
        entry = input(">> ")
        if entry == "quit":
            break
        split = entry.split(";")
        whitelist_entries.append((split[0].strip(), split[1].strip()))
    print()
    return whitelist_entries


def ui_create_subtasks_from_file(api, subtasks_path, root_task_id, project_id, task_type, work_type):
    print_heading("Defining Subtasks from File")
    create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type)


def print_heading(heading):
    print("=" * (len(heading) + 4))
    print("  {heading}  ".format(heading=heading))
    print("=" * (len(heading) + 4))


def ui_select_project(api, work_type):
    if work_type == DevWorkType.WORK:
        parent_id = WORK_PARENT_PROJECT_ID
    elif work_type == DevWorkType.PERSONAL:
        parent_id = PERSONAL_PARENT_PROJECT_ID
    else:
        raise ValueError(
            'work_type must use the DevWorkType enum and its value should be either WORK or PERSONAL')
    projects = api.get_projects()
    projects_with_parents = [p for p in projects if p.parent_id]
    projects = [
        (p.id, p.name) for p in projects_with_parents if int(p.parent_id) == parent_id
    ]
    choice = questionary.select(
        'Please select the project for the task', choices=sorted([p[1] for p in projects])).ask()
    return next((p for p in projects if p[1] == choice))


def ui_select_work_type():
    choice = questionary.select(
        "Choose a work type:",
        choices=[DevWorkType.WORK.name, DevWorkType.PERSONAL.name]
    ).ask()
    selected_work_type = DevWorkType[choice]
    return selected_work_type
