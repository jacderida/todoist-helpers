from enum import auto, Enum
from .labels import get_label_ids

class DevTaskType(Enum):
    ADMIN = auto()
    NON_CODE = auto()
    TERRAFORM = auto()
    RUST = auto()
    PYTHON = auto()

class DevWorkType(Enum):
    WORK = auto()
    PERSONAL = auto()

def create_subtasks_from_file(api, subtasks_path, project_id, root_task_id, task_type, work_type):
    with open(subtasks_path, 'r') as f:
        for line in f.readlines():
            name = line.strip()
            comment = ""
            if ";" in line:
                split = line.split(";")
                name = split[0].strip()
                comment = split[1].strip()
            create_subtask(api, name, project_id, task_type, work_type, root_task_id, comment=comment)

def create_terraform_merge_subtask(api, project_id, root_task_id, branch, target, task_type, work_type):
    create_merge_subtask(
        api, project_id, root_task_id, branch, "terraform", target, task_type, work_type)

def create_branch_subtask(api, project_id, root_task_id, task_type, work_type, repo, branch):
    create_subtask(
        api,
        "Create branch `{branch}` on `{repo}`".format(branch=branch, repo=repo),
        project_id,
        task_type,
        work_type,
        root_task_id)

def create_merge_subtask(api, project_id, root_task_id, branch, repo, target, task_type, work_type):
    merge_subtask = create_subtask(
        api,
        "Merge `{branch}` into `{target}` on `{repo}`".format(
            branch=branch, target=target, repo=repo),
        project_id,
        task_type,
        work_type,
        root_task_id)
    merge_subtask_id = merge_subtask["id"]
    if task_type == DevTaskType.RUST:
        create_subtask(
            api,
            "Run `cargo clippy` on `{branch}`".format(branch=branch),
            project_id,
            task_type,
            work_type,
            merge_subtask_id)
    create_subtask(
        api,
        "Rebase `master` into `{branch}`".format(branch=branch),
        project_id,
        task_type,
        work_type,
        merge_subtask_id)
    if task_type == DevTaskType.TERRAFORM:
        create_subtask(
            api,
            "Run a `terraform plan` for the `prod` environment",
            project_id,
            task_type,
            work_type,
            merge_subtask_id)
        create_subtask(
            api,
            "Run a `terraform plan` for the `int` environment",
            project_id,
            task_type,
            work_type,
            merge_subtask_id)
        create_subtask(
            api,
            "Run a `terraform plan` for the `perf` environment",
            project_id,
            task_type,
            work_type,
            merge_subtask_id)
    create_subtask(
        api,
        "Submit pull request for `{branch}`".format(branch=branch),
        project_id,
        task_type,
        work_type,
        merge_subtask_id)

def create_jira_admin_task(api, project_id, root_task_id, jira_ref):
    create_subtask(
        api,
        "Close `{jira_ref}`".format(jira_ref=jira_ref),
        project_id,
        DevTaskType.ADMIN,
        DevWorkType.WORK,
        root_task_id)

def create_parent_task(api, content, project_id, task_type, work_type, extra_labels=[], comment=""):
    return create_task(
        api, content, project_id, task_type, work_type, extra_labels=extra_labels, comment=comment)

def create_subtask(
        api, content, project_id, task_type, work_type, parent_id, extra_labels=[], comment=""):
    return create_task(
        api, content, project_id, task_type, work_type, parent_id, extra_labels, comment)

def create_task(
        api, content, project_id, task_type, work_type, parent_id=None, extra_labels=[], comment=""):
    due = None if parent_id else {"string": "Today"}
    task = api.items.add(
        content,
        project_id=project_id,
        parent_id=parent_id,
        due=due,
        labels=get_label_ids(api, get_labels_for_task(task_type, work_type, extra_labels)))
    api.commit()
    if parent_id:
        print("Created subtask '{name}'".format(name=task["content"]))
    else:
        print("Created task '{name}'".format(name=task["content"]))
    if comment:
        api.notes.add(task["id"], comment)
        api.commit()
        print("Added comment to '{name}'".format(name=task["content"]))
    return task

def get_labels_for_task(task_type, work_type, extra_labels):
    labels = []
    if work_type == DevWorkType.WORK:
        labels.append("work")
    elif work_type == DevWorkType.PERSONAL:
        labels.append("home")
    if task_type == DevTaskType.ADMIN:
        labels.append("admin")
    else:
        labels.append("development")
    return labels + extra_labels
