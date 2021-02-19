from labels import get_label_ids
from .tasks import create_subtask

def ui_get_jira_reference():
    print("Please supply the JIRA reference")
    jira_ref = input(">> ")
    return jira_ref

def ui_create_sub_tasks(api, root_task_id, project_id):
    while True:
        print("Please enter the name of a subtask to add (or enter 'quit' to stop)")
        name = input(">> ")
        if name == "quit":
            break
        create_subtask(api, name, project_id, root_task_id)

def ui_create_root_task(api, project_id, jira_ref):
    print("Please supply the name of the main task")
    name = input(">> ")
    print("Creating task '{name} [{jira_ref}]'".format(name=name, jira_ref=jira_ref))
    root_task = api.items.add(
        "{name} [{jira_ref}]".format(name=name, jira_ref=jira_ref),
        project_id=project_id,
        labels=get_label_ids(api, ["work", "development"]))
    api.commit()
    return root_task['id']
