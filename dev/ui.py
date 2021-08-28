import os

from .tasks import DevTaskType
from .tasks import DevWorkType
from .tasks import create_parent_task
from .tasks import create_subtask
from .tasks import create_subtasks_from_file
from .tasks import create_branch_subtask
from projects import get_valid_project_selection

WORK_PARENT_PROJECT_ID = 2235604758
PERSONAL_PARENT_PROJECT_ID = 2181705102

WORK_REPOS = [
    "qp2p",
    "safe_network",
    "self_update",
    "sn_api",
    "sn_authd",
    "sn_cli",
    "sn_testnet_tool"
]

PERSONAL_REPOS = [
    "tdl-rs",
    "todoist-helpers",
    "vagrant-boxes"
]

def ui_get_jira_or_branch_ref():
    print_heading("JIRA/Branch Reference")
    print("Please supply the JIRA ticket or branch name for the work")
    jira_ref = input(">> ")
    print()
    return jira_ref

def ui_create_subtasks(api, root_task_id, project_id, heading, subheading, task_type, work_type):
    print_heading(heading)
    print(subheading)
    while True:
        print("Please enter the name of the subtask to add")
        print("Enter 'quit' to stop adding subtasks")
        name = input(">> ")
        if name == "quit":
            break
        create_subtask(api, name, project_id, task_type, work_type, root_task_id)
    print()

def ui_create_root_dev_task(
        api, project_id, branch_ref, task_type, work_type, repos=[], extra_labels=[]):
    print_heading("Main Task Name")
    print("Use a name that reflects the outcome of the work")
    name = input(">> ")
    task_name = name
    jira_url = os.getenv("JIRA_BASE_URL")
    if jira_url:
        task_name = "[{jira_ref}]({jira_url}/{jira_ref}): {name}".format(
            jira_ref=branch_ref, jira_url=jira_url, name=name),
    root_task = create_parent_task(api, task_name, project_id, task_type, work_type, extra_labels=extra_labels)
    root_task_id = root_task["id"]
    for repo in repos:
        create_branch_subtask(api, project_id, root_task_id, task_name, work_type, repo, branch_ref)
    print()
    return root_task_id

def ui_create_root_dev_admin_task(api, project_id, work_type, extra_labels=[]):
    print_heading("Main Task Name")
    print("Use a name that reflects the outcome of the work")
    task_name = input(">> ")
    root_task = create_parent_task(
        api, task_name, project_id, DevTaskType.ADMIN, work_type, extra_labels=extra_labels)
    root_task_id = root_task["id"]
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

def ui_get_main_repo(work_type):
    print_heading("Main Repo")
    print("The following repos are available:")
    count = 1
    repos = get_repos(work_type)
    for repo in repos:
        print("{num}. {name}".format(num=count, name=repo))
        count += 1
    print("Select the repositories for this work using a comma separated list")
    selected = input(">> ")
    print()
    selected_repos = []
    if "," in selected:
        selected_repos = [repos[int(x) - 1] for x in selected.split(",")]
    else:
        selected_repos = [repos[int(selected) - 1]]
    return selected_repos

def ui_create_subtasks_from_file(api, subtasks_path, root_task_id, project_id, task_type, work_type):
    print_heading("Defining Subtasks from File")
    create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type)

def print_heading(heading):
    print("=" * (len(heading) + 4))
    print("  {heading}  ".format(heading=heading))
    print("=" * (len(heading) + 4))

def ui_select_project(api, work_type):
    print_heading("Select Project")
    print("Please select the project to work with: ")
    parent_id = 0
    if work_type == DevWorkType.WORK:
        parent_id = WORK_PARENT_PROJECT_ID
    elif work_type == DevWorkType.PERSONAL:
        parent_id = PERSONAL_PARENT_PROJECT_ID
    projects = {
        p['name']:p['id']
        for p in api.state['projects'] if p['parent_id'] == parent_id
    }
    count = 1
    sorted_project_names = sorted(projects.keys())
    for project in sorted_project_names:
        print("{num}. {project_name}".format(num=count, project_name=project))
        count += 1
    selected_project_name = get_valid_project_selection(sorted_project_names)
    print("Working with project {project}".format(project=selected_project_name))
    print()
    return (selected_project_name, projects[selected_project_name])

def get_repos(work_type):
    repos = []
    if work_type == DevWorkType.WORK:
        repos = WORK_REPOS
    elif work_type == DevWorkType.PERSONAL:
        repos = PERSONAL_REPOS
    return repos

