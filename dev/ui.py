import os

from .tasks import create_parent_task
from .tasks import create_subtask
from .tasks import create_subtasks_from_file
from .tasks import create_branch_subtask

REPOS = [
    "qp2p",
    "safe_network",
    "sn_authd",
    "sn_cli"
]

def ui_get_jira_or_branch_ref():
    print_heading("JIRA/Branch Reference")
    print("Please supply the JIRA ticket or branch name for the work")
    jira_ref = input(">> ")
    print()
    return jira_ref

def ui_create_subtasks(api, root_task_id, project_id, heading, subheading):
    print_heading(heading)
    print(subheading)
    while True:
        print("Please enter the name of the subtask to add")
        print("Enter 'quit' to stop adding subtasks")
        name = input(">> ")
        if name == "quit":
            break
        create_subtask(api, name, project_id, root_task_id)
    print()

def ui_create_root_task(api, project_id, branch_ref, repos=[], extra_labels=[]):
    print_heading("Main Task Name")
    print("Use a name that reflects the outcome of the work")
    name = input(">> ")
    task_name = name
    jira_url = os.getenv("JIRA_BASE_URL")
    if jira_url:
        task_name = "[{jira_ref}]({jira_url}/{jira_ref}): {name}".format(
            jira_ref=branch_ref, jira_url=jira_url, name=name),
    root_task = create_parent_task(api, task_name, project_id, ["work", "development"] + extra_labels)
    root_task_id = root_task["id"]
    for repo in repos:
        create_branch_subtask(api, project_id, root_task_id, repo, branch_ref)
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

def ui_get_main_repo():
    print_heading("Main Repo")
    print("The following repos are available:")
    count = 1
    for repo in REPOS:
        print("{num}. {name}".format(num=count, name=repo))
        count += 1
    print("Select the repositories for this work using a comma separated list")
    selected = input(">> ")
    print()
    selected_repos = []
    if "," in selected:
        selected_repos = [REPOS[int(x) - 1] for x in selected.split(",")]
    else:
        selected_repos = [REPOS[int(selected) - 1]]
    return selected_repos

def ui_create_subtasks_from_file(api, subtasks_path, root_task_id, project_id):
    print_heading("Defining Subtasks from File")
    create_subtasks_from_file(api, subtasks_path, root_task_id, project_id)

def print_heading(heading):
    print("=" * (len(heading) + 4))
    print("  {heading}  ".format(heading=heading))
    print("=" * (len(heading) + 4))
