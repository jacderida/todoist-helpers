#!/usr/bin/env python

import os
import re
import subprocess
import sys

from lib.tasks import get_outstanding_dev_tasks, DevWorkType
from lib.ui import ui_select_repository

import questionary
from github import Github
from rich.console import Console
from todoist.api import TodoistAPI

console = Console()

def select_dev_task(tasks):
    choice = questionary.select(
        'Please select the dev task to submit for PR',
        choices=[t.name for t in tasks if t.due_info]
    ).ask()
    return next((t for t in tasks if t.name == choice))

def process_merge_checklist(api, console, merge_tasks):
    choices = [{'name': t.name} for t in merge_tasks]
    questionary.checkbox(
        'Complete the merge checklist',
        choices=choices,
        validate=lambda answers: (
            True if len(answers) == len(choices) else 'All items on the checklist must be completed'
        )
    ).ask()
    with console.status('[bold green]Completing checklist items on Todoist...') as _:
        for task in merge_tasks:
            console.print("Marking '{}' as complete".format(task.name))
            task.complete(api)

def get_pr_body(repo_path):
    body = subprocess.run([
        'git', 'log', '--format=format:- %h **%s**%n%n%w(0,2,2)%b', '--reverse', 'origin/HEAD..HEAD'
    ], stdout=subprocess.PIPE, cwd=repo_path).stdout.decode('utf-8')
    return body

def get_head_branch(repo_path):
    branch = subprocess.run(
        ['git', 'branch', '--show-current'],
        stdout=subprocess.PIPE,
        cwd=repo_path).stdout.decode('utf-8')
    return branch.strip()

def get_pr_title(body):
    # The regex matches these types of lines in the body:
    # - 72988e92f **feat: extend `nrs register` with more output**
    # It's parsing the text between the opening and closing ** characters.
    matches = re.findall(r'-.*\*\*(.*)\*\*', body, re.MULTILINE)
    selected = questionary.checkbox(
        'Select ONE of the following commit messages for the PR title. \n' \
        'If none of these choices are appropriate, do not select any of them.',
        choices=matches
    ).ask()
    if selected:
        title = selected[0]
    else:
        title = questionary.text(
            'Please supply the title for the PR:',
            validate=lambda answer: (
                True if len(answer) > 5 else 'Please provide a title with at least 5 characters'
            )
        ).ask()
    return title

def submit_pr(source_owner, title, body, head_branch):
    (owner, repo_path) = ui_select_repository('Select Target Repository')
    parts = str(repo_path).split('/')
    repo = parts[len(parts) - 1]
    head = f'{source_owner}:{head_branch}' if source_owner != owner else head_branch

    url = f'https://github.com/{owner}/{repo}/pull'
    with console.status(f'[bold green]Submitting pull request to {owner}/{repo}...') as _:
        github_pat = os.getenv('GITHUB_PAT')
        github = Github(github_pat)
        repo = github.get_repo(f'{owner}/{repo}')
        pr = repo.create_pull(title=title, body=body, base='main', head=head)
        url = url + '/{}'.format(pr.number)
    print(f'The PR was created and can be accessed at: {url}')
    return url

def create_pr():
    (source_owner, repo_path) = ui_select_repository('Select Source Repository')
    print(f'selected repository at {repo_path}')
    body = get_pr_body(repo_path)
    title = get_pr_title(body)
    head_branch = get_head_branch(repo_path)
    return submit_pr(source_owner, title, body, head_branch)

def main():
    with console.status('[bold green]Initial Todoist API sync...') as _:
        api_token = os.getenv('TODOIST_API_TOKEN')
        api = TodoistAPI(api_token)
        api.sync()
    dev_tasks = []
    with console.status('[bold green]Getting outstanding development tasks...') as _:
        dev_tasks = get_outstanding_dev_tasks(api, DevWorkType.WORK)
    task = select_dev_task(dev_tasks)
    if len(task.subtasks) > 1:
        console.print(
            '[bold red]Error:[/bold red] A task is only eligible for merge ' \
            'if all subtasks (except the merge task) are cleared.'
        )
        console.print(
            '[bold green]Suggestion:[/bold green] Clear all the non-merge subtasks first.'
        )
        return 1;
    merge_subtask = task.subtasks[0]
    if not merge_subtask.name.startswith('Merge'):
        console.print(
            "[bold red]Error:[/bold red] The selected task has a remaining subtask, " \
            "but it's not a merge task."
        )
        console.print(
            '[bold green]Suggestion:[/bold green] Select a mergeable task to work with.'
        )
        return 1
    process_merge_checklist(api, console, merge_subtask.subtasks)
    url = create_pr()
    with console.status('[bold green]Updating development task...') as _:
        task.mark_waiting(api, f'PR submitted, now waiting for review. PR is available at: {url}')

if __name__ == '__main__':
    sys.exit(main())
