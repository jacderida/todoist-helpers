#!/usr/bin/env python

import ast
import os
import sys

from todoist_api_python.api import TodoistAPI
from lib.labels import get_full_label_names
from lib.ui import ui_select_project, ui_select_work_type


def create_section(project, api):
    section_name = input("Please enter the name of the section to add:\n")
    section = api.add_section(name=section_name, project_id=project[0])
    print(f"Added {section.name} section to {project[1]} project")
    return section


def parse_line(line):
    split = line.strip().split(";")
    task_name = split[0].strip()
    is_sub_task = True if task_name[0] == "-" else False
    labels = ast.literal_eval(split[1].strip())
    task_name = task_name[1:].strip() # remove leading '* ' or '- ' from task name
    return (task_name, [l.strip() for l in labels], is_sub_task)


def add_tasks_from_file(api, path, project, section):
    with open(path) as f:
        parent_id = None
        for line in f.readlines():
            task_name, labels, is_sub_task = parse_line(line)
            label_names = get_full_label_names(api, labels)
            if not is_sub_task:
                print(f"Adding '{task_name}' task to '{section.name}' section")
                task = api.add_task(
                    content=task_name,
                    project_id=project[0],
                    section_id=section.id,
                    labels=label_names)
                parent_id = task.id
            else:
                print(f"Adding '{task_name}' subtask to '{section.name}' section")
                api.add_task(
                    content=task_name,
                    project_id=project[0],
                    section_id=section.id,
                    labels=label_names,
                    parent_id=parent_id)


def get_input_file_from_args():
    if len(sys.argv) < 2:
        print("A file with a list of tasks must be specified")
        sys.exit(1)
    input_file_path = sys.argv[1]
    if not os.path.exists(input_file_path):
        print("{path} does not exist".format(path=input_file_path))
        sys.exit(1)
    if not os.path.isfile(input_file_path):
        print("{path} must be a file and not a directory".format(path=input_file_path))
        sys.exit(1)
    return input_file_path


def main():
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)

    input_task_file_path = get_input_file_from_args()
    work_type = ui_select_work_type()
    project = ui_select_project(api, work_type)
    section = create_section(project, api)
    add_tasks_from_file(api, input_task_file_path, project, section)
    return 0


if __name__ == "__main__":
    sys.exit(main())
