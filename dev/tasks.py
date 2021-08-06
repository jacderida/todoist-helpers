from labels import get_label_ids

def create_subtasks_from_file(api, subtasks_path, project_id, root_task_id):
    with open(subtasks_path, 'r') as f:
        for line in f.readlines():
            name = line.strip()
            comment = ""
            if ";" in line:
                split = line.split(";")
                name = split[0].strip()
                comment = split[1].strip()
            create_subtask(api, name, project_id, root_task_id, comment=comment)

def create_terraform_merge_subtask(api, project_id, root_task_id, branch, target):
    create_merge_subtask(
        api, project_id, root_task_id, branch, "terraform", target, terraform_repo=True)

def create_branch_subtask(api, project_id, root_task_id, repo, branch):
    create_subtask(
        api,
        "Create branch `{branch}` on `{repo}`".format(branch=branch, repo=repo),
        project_id,
        root_task_id)

def create_merge_subtask(api, project_id, root_task_id, branch, repo, target, terraform_repo=False):
    merge_subtask = create_subtask(
        api,
        "Merge `{branch}` into `{target}` on `{repo}`".format(
            branch=branch, target=target, repo=repo),
        project_id,
        root_task_id)
    merge_subtask_id = merge_subtask["id"]
    create_subtask(
        api,
        "Run `cargo clippy` on `{branch}`".format(branch=branch),
        project_id,
        merge_subtask_id)
    create_subtask(
        api,
        "Rebase `master` into `{branch}`".format(branch=branch),
        project_id,
        merge_subtask_id)
    if terraform_repo:
        create_subtask(
            api,
            "Run a `terraform plan` for the `prod` environment",
            project_id,
            merge_subtask_id)
        create_subtask(
            api,
            "Run a `terraform plan` for the `int` environment",
            project_id,
            merge_subtask_id)
        create_subtask(
            api,
            "Run a `terraform plan` for the `perf` environment",
            project_id,
            merge_subtask_id)
    create_subtask(
        api,
        "Submit pull request for `{branch}`".format(branch=branch),
        project_id,
        merge_subtask_id)

def create_jira_admin_task(api, project_id, root_task_id, jira_ref):
    create_subtask(
        api,
        "Close `{jira_ref}`".format(jira_ref=jira_ref),
        project_id,
        root_task_id,
        ["work", "admin"])

def create_parent_task(api, content, project_id, labels=["work", "development"], comment=""):
    return create_task(
        api, content, project_id, None, labels, comment)

def create_subtask(api, content, project_id, parent_id, labels=["work", "development"], comment=""):
    return create_task(
        api, content, project_id, parent_id, labels, comment)

def create_task(api, content, project_id, parent_id=None, labels=["work", "development"], comment=""):
    due = None
    if not parent_id: due = {"string": "Today"}
    task = api.items.add(
        content,
        project_id=project_id,
        parent_id=parent_id,
        due=due,
        labels=get_label_ids(api, labels))
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
