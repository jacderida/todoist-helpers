#!/usr/bin/env python

"""
Parses a day outline in a given file and adds each line as a task. Here is an example file:
11:00:00; Day Outline; Morning Work [1.5 hours]; ['work', 'development']
12:30:00; Day Outline; Exercise and Lunch [1 hours]; ['exercise', 'personal-wellbeing']
13:30:00; Meetings; Modern on LCMS [0.5 hours]; ['work', 'call']
14:00:00; Meetings; ODSC Management Meeting [0.5 hours]; ['work', 'call']
14:30:00; Meetings; Azure Walkthrough [1 hour]; ['work', 'call']
15:30:00; Day Outline; Afternoon Work [4 hours]; ['work', 'development']
19:30:00; Day Outline; Shutdown Checklist [0.5 hours]; ['work', 'admin'] 

The columns are time, project name, content (task name), labels.
"""

import ast
import os
import sys

from datetime import datetime, timedelta

from todoist.api import TodoistAPI

from labels import get_label_ids
from projects import get_project_id

api_token = os.getenv("TODOIST_API_TOKEN")
api = TodoistAPI(api_token)
api.sync()

def parse_labels(label_string):
    labels = ast.literal_eval(label_string)
    return [l.strip() for l in labels]

def main(outline_path):
    tomorrow = datetime.strftime(datetime.now() + timedelta(days=1), "%Y-%m-%d")
    with open(outline_path) as f:
        for line in f.readlines():
            split = line.split(";")
            time = split[0].strip()
            content = split[1].strip()
            project = split[2].strip()
            labels = split[3].strip()
            project_id = get_project_id(api, project)
            print("{}: {} to {}".format(time, content, project))
            api.items.add(
                project_id=project_id,
                content=content,
                due={"date": "{}T{}".format(tomorrow, time)},
                labels=get_label_ids(api, parse_labels(labels)))
    api.commit()

if __name__ == "__main__":
    outline_path = ""
    if len(sys.argv) >= 2:
        outline_path = sys.argv[1]
    sys.exit(main(outline_path))
