#!/usr/bin/env python

"""
This script can be used in two different ways.

If using it late in the day, e.g., at 2330, run:
./clear-today.py

This will clear all work, personal and routine tasks that weren't completed and are either overdue
or due today. For daily routine tasks, Todoist will set their due date to tomorrow. Any non-routine
tasks need their new date assigned as part of a planning session; they aren't simply carried over.

If using it in the early hours of the morning, e.g., at 0130, run:
./clear-today.py --today

This has the same result as above, except it explicitly sets the due date of daily routine tasks to
today. If left to Todoist, it would set the due date to tomorrow, i.e., the next calendar day, which
probably isn't desired. Use the `--today` flag if you want to address the routine tasks in the
current calendar day when you're next awake.
"""

import os
import sys
from datetime import datetime

from todoist.api import TodoistAPI

ACTIVE_PERSONAL_PROJECTS_ID = 2181705102 # ID of parent project for all personal projects
ACTIVE_WORK_PROJECTS_ID = 2235604758 # ID of parent project for all work projects
ROUTINE_PROJECTS_ID = 2235762094 # ID of parent project for all routine projects
DAY_OUTLINE_PROJECT_ID = 2279298884

def parse_due_date(due_date):
    try:
        return datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return datetime.strptime(due_date, '%Y-%m-%d')

def get_due_or_overdue_tasks(api, parent_id):
    active_work_project_ids = [
        p['id'] for p in api.state['projects'] if p['parent_id'] == parent_id
    ]
    tasks_with_due_dates = []
    for id in active_work_project_ids:
        project = api.projects.get_data(id)
        tasks_with_due_dates.extend([t for t in project['items'] if t['due']])
    return tasks_with_due_dates

def clear_due_dates(api, tasks, use_today=False):
    """
    The intention here is to clear the due dates from any overdue tasks or those due today.

    The `due` key on `item` isn't just a date string: it's a dictionary containing the due date
    and any recurrence info, e.g., "every workday". Setting the `date` key to `None` will clear
    *this* occurrence, but any recurrence info will be retained. If, for example, the task has an
    "every day" recurrence, clearing the date means the task is now due tomorrow.

    If we're clearing out yesterday's tasks in the early hours of the morning, we may want the
    routine tasks set with today's date, so you can do them during the current day when you next
    wake up. In this case, use the `--today` flag and 'use_today' will be `true`.

    Another note on `--today`: when used, only tasks that recurr every day, or every work day, will
    have their due date explicitly set to today. Otherwise we'll let Todoist take care of setting
    the next due date, which may not happen to be today.
    """
    for task in tasks:
        item = api.items.get_by_id(task['id'])
        due = item['due']
        due_date = parse_due_date(due['date'])
        if due_date < datetime.now():
            if use_today and due['string'] in ['every day', 'every work day']:
                print('Clearing current due date on "{}"'.format(task['content']))
                due['date'] = datetime.strftime(datetime.now(), "%Y-%m-%d")
            else:
                print('Clearing current due date on "{}"'.format(task['content']))
                due['date'] = None
            item.update(due=due)
    api.commit()

def delete_day_outline_tasks(api):
    print("Deleting current Day Outline tasks...")
    project = api.projects.get_data(DAY_OUTLINE_PROJECT_ID)
    for task in project['items']:
        print('Deleting "{}"'.format(task['content']))
        item = api.items.get_by_id(task['id'])
        item.delete()
    api.commit()

def main(use_today):
    api_token = os.getenv('TODOIST_API_TOKEN')
    api = TodoistAPI(api_token)
    api.sync()
    print("WARNING: This will clear today's (or overdue) routine tasks without completing them.")
    print("If you want to have them count towards today's total count, stop this script and mark them completed.")
    print("Otherwise, press any key to continue...")
    input(">> ")
    print("Clearing any work tasks...")
    work_tasks = get_due_or_overdue_tasks(api, ACTIVE_WORK_PROJECTS_ID)
    clear_due_dates(api, work_tasks)
    print()
    print("Clearing any personal tasks...")
    personal_tasks = get_due_or_overdue_tasks(api, ACTIVE_PERSONAL_PROJECTS_ID)
    clear_due_dates(api, personal_tasks)
    print()
    print("Clearing any routine tasks...")
    routine_tasks = get_due_or_overdue_tasks(api, ROUTINE_PROJECTS_ID)
    clear_due_dates(api, routine_tasks, use_today)
    print()
    delete_day_outline_tasks(api)

if __name__ == '__main__':
    use_today = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "--today":
            use_today = True
    sys.exit(main(use_today))
