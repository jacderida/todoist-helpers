from labels import get_label_ids

def create_terraform_merge_subtask(api, project_id, root_task_id, branch, target):
    create_merge_subtask(
        api, project_id, root_task_id, branch, "terraform", target, terraform_repo=True)

def create_merge_subtask(api, project_id, root_task_id, branch, repo, target, terraform_repo=False):
    merge_subtask = create_subtask(
        api,
        "Merge `{branch}` into `{target}` on `{repo}`".format(
            branch=branch, target=target, repo=repo),
        project_id,
        root_task_id)
    if terraform_repo:
        create_subtask(
            api,
            "Run a `terraform plan` for the `prod` environment",
            project_id,
            merge_subtask["id"])
        create_subtask(
            api,
            "Run a `terraform plan` for the `int` environment",
            project_id,
            merge_subtask["id"])
    create_subtask(
        api,
        "Submit pull request for `{branch}`".format(branch=branch),
        project_id,
        merge_subtask["id"])

def create_subtask(api, content, project_id, parent_id):
    subtask = api.items.add(
        content,
        project_id=project_id,
        parent_id=parent_id,
        labels=get_label_ids(api, ["work", "development"]))
    api.commit()
    print("Created subtask '{name}'".format(name=subtask["content"]))
    return subtask
