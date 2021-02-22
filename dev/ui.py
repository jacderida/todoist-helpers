from labels import get_label_ids
from .tasks import create_subtask
from .tasks import create_branch_subtask

def ui_get_jira_reference():
    print_heading("JIRA Reference")
    print("Please supply the JIRA story or ticket reference for the work")
    jira_ref = input(">> ")
    print()
    return jira_ref

def ui_create_sub_tasks(api, root_task_id, project_id, heading, subheading):
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

def ui_create_root_task(api, project_id, jira_ref, repo):
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
    create_branch_subtask(api, project_id, root_task_id, repo, jira_ref)
    print()
    return root_task_id

# def ui_get_repos():
    # repos = [
        # "ansible",
        # "ansible_modern",
        # "dcf",
        # "eunomia"
    # ]
    # print("The following repos are available:")
    # count = 1
    # for repo in repos:
        # print("{num}. {name}".format(num=count, name=repo))
        # count += 1
    # print("Use a comma separated list to select the repos to use for this task")
    # selected = input(">> ")
    # print()
    # return [repos[int(x) - 1] for x in selected.split(",")]

def print_heading(heading):
    print("=" * (len(heading) + 4))
    print("  {heading}  ".format(heading=heading))
    print("=" * (len(heading) + 4))
