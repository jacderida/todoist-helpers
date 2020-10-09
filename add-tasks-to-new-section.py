#!/usr/bin/env python

import ast
import os
import sys

from todoist.api import TodoistAPI

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

def create_section(project_id):
    section_name = input('Please enter the name of the section to add:\n')
    section = api.sections.add(section_name, project_id=project_id)
    return section

def get_valid_project_selection(projects):
    print("Please enter the number of the project to add the section to: ")
    while True:
        selection = input()
        try:
            numeric_selection = int(selection)
            if numeric_selection < 1 or numeric_selection > len(projects):
                print('Please enter a value between 1 and {0}.'.format(len(projects)))
                continue
            return projects[numeric_selection - 1]
        except ValueError:
            print('Please enter a value between 1 and {}.'.format(len(projects)))

def get_user_project_selection():
    projects = { p['name']:p['id'] for p in api.state['projects'] }
    count = 1
    sorted_project_names = sorted(projects.keys())
    for project in sorted_project_names:
        print("{num}. {project_name}".format(num=count, project_name=project))
        count += 1
    selected_project_name = get_valid_project_selection(sorted_project_names)
    return (selected_project_name, projects[selected_project_name])

def parse_line(line):
    split = line.strip().split(';')
    labels = ast.literal_eval(split[1].strip())
    return (split[0], [l.strip() for l in labels])

def add_tasks_from_file(path, project, section):
    print("Adding {section} section to {project} project".format(
        section=section['name'], project=project[0]))
    with open(path) as f:
        for line in f.readlines():
            task_name, labels = parse_line(line)
            label_ids = get_label_ids(labels)
            print("Adding {task_name} task to {section} section".format(
                task_name=task_name, section=section['name']))
            api.items.add(
                task_name, project_id=project[1], section_id=section['id'], labels=label_ids)

def get_label_ids(labels):
    label_ids = []
    for label in labels:
        try:
            retrieved_label = next(x for x in api.state['labels'] if label in x['name'])
        except StopIteration:
            print("Label '{label}' doesn't exist. Please respecify with a valid label.".format(
                label=label))
            sys.exit(1)
        label_ids.append(retrieved_label['id'])
    return label_ids

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
    project = get_user_project_selection()
    section = create_section(project[1])
    add_tasks_from_file(input_task_file_path, project, section)
    api.commit()

if __name__ == '__main__':
    sys.exit(main())
