#!/usr/bin/env python

import ast
import os
import sys

from todoist.api import TodoistAPI
from labels import get_label_ids
from projects import ui_select_project

api_token = os.getenv("TODOIST_API_TOKEN")
api = TodoistAPI(api_token)
api.sync()

def create_section(project_id):
    section_name = input("Please enter the name of the section to add:\n")
    section = api.sections.add(section_name, project_id=project_id)
    return section

def parse_line(line):
    split = line.strip().split(";")
    task_name = split[0].strip()
    is_sub_task = True if task_name[0] == "-" else False
    labels = ast.literal_eval(split[1].strip())
    task_name = task_name[1:].strip() # remove leading '* ' or '- ' from task name
    return (task_name, [l.strip() for l in labels], is_sub_task)

def add_tasks_from_file(path, project, section):
    print("Adding {section} section to {project} project".format(
        section=section["name"], project=project[0]))
    with open(path) as f:
        parent_id = None
        for line in f.readlines():
            task_name, labels, is_sub_task = parse_line(line)
            label_ids = get_label_ids(api, labels)
            if not is_sub_task:
                print("Adding {task_name} task to {section} section".format(
                    task_name=task_name, section=section["name"]))
                item = api.items.add(
                    task_name, project_id=project[1], section_id=section["id"], labels=label_ids)
                parent_id = item["id"]
            else:
                print("Adding {task_name} subtask to {section} section".format(
                    task_name=task_name, section=section["name"]))
                api.items.add(
                    task_name,
                    project_id=project[1],
                    section_id=section["id"],
                    labels=label_ids,
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
    input_task_file_path = get_input_file_from_args()
    project = ui_select_project(api)
    section = create_section(project[1])
    add_tasks_from_file(input_task_file_path, project, section)
    api.commit()

if __name__ == "__main__":
    sys.exit(main())
