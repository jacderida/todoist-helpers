from enum import auto, Enum
from .labels import get_label_ids, get_label_id

from rich.console import Console

ACTIVE_PERSONAL_PROJECTS_ID = (
    2181705102  # ID of parent project for all personal projects
)
ACTIVE_WORK_PROJECTS_ID = 2235604758  # ID of parent project for all work projects

console = Console()


class Task:
    def __init__(self, id, name, project, labels, due_info):
        self.id = id
        self.name = name
        self.project = project
        self.labels = labels
        self.due_info = due_info
        self.subtasks = []

    def add_subtask(self, id, name, labels, due_info):
        task = Task(id, name, self.project, labels, due_info)
        self.subtasks.append(task)
        return task

    def complete(self, api):
        item = api.items.get_by_id(self.id)
        item.complete()
        api.commit()

    def mark_waiting(self, api, comment):
        item = api.items.get_by_id(self.id)
        self.labels.append(get_label_id(api, "waiting"))
        item.update(labels=self.labels)
        api.notes.add(self.id, comment)
        api.commit()


class DevTaskType(Enum):
    ADMIN = auto()
    INVESTIGATION = auto()
    NON_MERGE = auto()
    TERRAFORM = auto()
    RUST = auto()
    PYTHON = auto()


class DevWorkType(Enum):
    WORK = auto()
    PERSONAL = auto()


def get_outstanding_dev_tasks(api, work_type):
    if work_type == DevWorkType.WORK:
        parent_id = ACTIVE_WORK_PROJECTS_ID
    elif work_type == DevWorkType.PERSONAL:
        parent_id = ACTIVE_PERSONAL_PROJECTS_ID
    else:
        raise ValueError(
            "work_type must use the DevWorkType enum and its value should be either WORK or PERSONAL"
        )

    project_info = [
        (p["id"], p["name"])
        for p in api.state["projects"]
        if p["parent_id"] == parent_id
    ]
    label_id = get_label_id(api, "development")
    tasks = []
    for (project_id, project_name) in project_info:
        project_data = api.projects.get_data(project_id)
        root_tasks = [
            t
            for t in project_data["items"]
            if label_id in t["labels"] and not t["parent_id"]
        ]
        for root_task in root_tasks:
            task = Task(
                root_task["id"],
                root_task["content"],
                (project_id, project_name),
                root_task["labels"],
                root_task["due"],
            )
            populate_subtasks(task, project_data)
            tasks.append(task)
    return tasks


def populate_subtasks(task, project_data):
    sub_tasks = [t for t in project_data["items"] if t["parent_id"] == task.id]
    for st in sub_tasks:
        sub_task = task.add_subtask(st["id"], st["content"], st["labels"], st["due"])
        populate_subtasks(sub_task, project_data)


def create_subtasks_from_file(
    api, subtasks_path, project_id, root_task_id, task_type, work_type
):
    with open(subtasks_path, "r") as f:
        for line in f.readlines():
            name = line.strip()
            comment = ""
            if ";" in line:
                split = line.split(";")
                name = split[0].strip()
                comment = split[1].strip()
            create_subtask(
                api,
                name,
                project_id,
                task_type,
                work_type,
                root_task_id,
                comment=comment,
            )


def create_terraform_merge_subtask(
    api, project_id, root_task_id, branch, target, task_type, work_type
):
    create_merge_subtask(
        api, project_id, root_task_id, branch, "terraform", target, task_type, work_type
    )


def create_branch_subtask(
    api, project_id, root_task_id, task_type, work_type, repo, branch
):
    create_subtask(
        api,
        "Create branch `{branch}` on `{repo}`".format(branch=branch, repo=repo),
        project_id,
        task_type,
        work_type,
        root_task_id,
    )


def create_pr_checklist_subtask(
    api, project_id, root_task_id, branch, task_type, work_type
):
    pr_checklist_subtask = create_subtask(
        api, "Perform PR checklist", project_id, task_type, work_type, root_task_id
    )
    pr_checklist_subtask_id = pr_checklist_subtask["id"]
    if task_type == DevTaskType.RUST:
        create_subtask(
            api,
            "Run `cargo clippy` on `{branch}`".format(branch=branch),
            project_id,
            task_type,
            work_type,
            pr_checklist_subtask_id,
        )
    create_subtask(
        api,
        "Create final commit",
        project_id,
        task_type,
        work_type,
        pr_checklist_subtask_id,
    )
    create_subtask(
        api,
        "Review commits for potential squash",
        project_id,
        task_type,
        work_type,
        pr_checklist_subtask_id,
    )
    create_subtask(
        api,
        "Carefully proof read commits",
        project_id,
        task_type,
        work_type,
        pr_checklist_subtask_id,
    )
    create_subtask(
        api,
        "Rebase `main` into `{branch}`".format(branch=branch),
        project_id,
        task_type,
        work_type,
        pr_checklist_subtask_id,
    )


def create_merge_subtasks(
    api, project_id, root_task_id, branch, repo, target, task_type, work_type
):
    create_subtask(
        api,
        f"Submit pull request for `{branch}`",
        project_id,
        task_type,
        work_type,
        root_task_id,
    )
    create_subtask(
        api,
        f"Merge `{branch}` into `{target}` on `{repo}`",
        project_id,
        task_type,
        work_type,
        root_task_id,
    )


def create_jira_admin_task(api, project_id, root_task_id, jira_ref):
    create_subtask(
        api,
        f"Close `{jira_ref}`",
        project_id,
        DevTaskType.ADMIN,
        DevWorkType.WORK,
        root_task_id,
    )


def create_parent_task(
    api, content, project_id, task_type, work_type, extra_labels=[], comment=""
):
    return create_task(
        api,
        content,
        project_id,
        task_type,
        work_type,
        extra_labels=extra_labels,
        comment=comment,
    )


def create_subtask(
    api,
    content,
    project_id,
    task_type,
    work_type,
    parent_id,
    extra_labels=[],
    comment="",
):
    return create_task(
        api, content, project_id, task_type, work_type, parent_id, extra_labels, comment
    )


def create_task(
    api,
    content,
    project_id,
    task_type,
    work_type,
    parent_id=None,
    extra_labels=[],
    comment="",
    apply_date=True,
):
    with console.status("[bold green]Creating task on Todoist...") as _:
        due = None
        if apply_date:
            due = None if parent_id else {"string": "Today"}
        task = api.items.add(
            content,
            project_id=project_id,
            parent_id=parent_id,
            due=due,
            labels=get_label_ids(
                api, get_labels_for_task(task_type, work_type, extra_labels)
            ),
        )
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
        labels.append("development")
    elif work_type == DevWorkType.PERSONAL:
        labels.append("home")
        labels.append("development")
    if task_type == DevTaskType.ADMIN:
        labels.append("admin")
        labels.append("development")
    if task_type == DevTaskType.INVESTIGATION:
        labels.append("investigation")
        labels.append("development")
    return labels + extra_labels
