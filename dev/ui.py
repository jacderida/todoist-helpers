from labels import get_label_ids
from .tasks import create_subtask
from .tasks import create_subtasks_from_file
from .tasks import create_branch_subtask

REPOS = [
    "ansible",
    "ansible_modern",
    "cda",
    "cps_stacks",
    "dcf",
    "eunomia",
    "terraform",
    "terraform_modern"
]

def ui_get_jira_reference():
    print_heading("JIRA Reference")
    print("Please supply the JIRA story or ticket reference for the work")
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

def ui_create_root_task(api, project_id, jira_ref, repos):
    print_heading("Main Task Name")
    print("Use a name that reflects the outcome of the work")
    name = input(">> ")
    print("Creating task '{jira_ref}: {name}'".format(jira_ref=jira_ref, name=name))
    root_task = api.items.add(
        "{jira_ref}: {name}".format(jira_ref=jira_ref, name=name),
        project_id=project_id,
        labels=get_label_ids(api, ["work", "development"]))
    api.commit()
    root_task_id = root_task["id"]
    for repo in repos:
        create_branch_subtask(api, project_id, root_task_id, repo, jira_ref)
    print()
    return root_task_id

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
