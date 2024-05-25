#!/usr/bin/env python

import os
import sys

from lib.tasks import create_parent_task, create_subtask, TaskType, WorkType
from todoist_api_python.api import TodoistAPI

import questionary
from rich.console import Console

MAINTENANCE_PROJECT_ID = 2331596593

console = Console()

def main():
    work_type = WorkType.WORK
    task_type = TaskType.DEV

    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)
    name = questionary.text(
        "What is the name of the testnet:",
        validate=lambda answer: True if len(answer) > 0 else "A name for the testnet must be provided"
    ).ask()
    faucet_address = questionary.text(
        "Provide the faucet address:",
        validate=lambda answer: True if len(answer) > 0 else "The faucet address must be provided"
    ).ask()
    peer = questionary.text(
        "Provide a peer:",
        validate=lambda answer: True if len(answer) > 0 else "A peer must be provided"
    ).ask()
    parent = create_parent_task(
        api, f"Smoke test for `{name}`", MAINTENANCE_PROJECT_ID, task_type, work_type)
    create_subtask(
        api,
        "Create an Ubuntu 22.04 VM",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment="""
cd /home/chris/dev/github.com/jacderida/vagrant-boxes/base-ubuntu-22.04
vagrant up
        """
    )
    create_subtask(
        api,
        "Install safeup",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment="curl -sSL https://raw.githubusercontent.com/maidsafe/safeup/main/install.sh | bash")
    create_subtask(
        api,
        "Install safe",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment="safeup client")
    create_subtask(
        api,
        "Get tokens from the faucet",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment=f"safe --peer {peer} wallet get-faucet {faucet_address}")
    create_subtask(
        api,
        "Download the Ubuntu netboot archive",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment="""
curl -L -O https://mirror.lon.macarne.com/ubuntu-releases/24.04/ubuntu-24.04-netboot-amd64.tar.gz
        """)
    create_subtask(
        api,
        "Upload the Ubuntu netboot archive",
        MAINTENANCE_PROJECT_ID,
        task_type,
        work_type,
        parent.id,
        comment=f"safe files upload ubuntu-24.04-netboot-amd64.tar.gz")

if __name__ == '__main__':
    sys.exit(main())
