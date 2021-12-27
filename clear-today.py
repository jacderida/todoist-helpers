#!/usr/bin/env python

import os
import sys
from datetime import datetime

from todoist.api import TodoistAPI

ACTIVE_PERSONAL_PROJECTS_ID = 2181705102 # ID of parent project for all personal projects
ACTIVE_WORK_PROJECTS_ID = 2235604758 # ID of parent project for all work projects
ROUTINE_PROJECTS_ID = 2235762094 # ID of parent project for all routine projects
DAY_OUTLINE_PROJECT_ID = 2279298884
HOUSEWORK_PROJECT_ID = 2231549968

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

    The 'due' field on the item isn't just a date string, it also contains information about
    the recurrence frequency for recurring tasks, e.g. "every workday". Setting the 'date'
    field of the due date to None has the effect of clearing out the date, but the recurrence
    information will be retained. If for example the task was setup with an "every day"
    recurrence, clearing the 'date' field means the task will now be due tomorrow.

    If you're clearing out yesterday's tasks in the early hours of the morning, it may be desirable
    to have the routine tasks set with today's date, so you can do them during the current day when
    you next wake up. In this case, the `--today` flag will be used and 'use_today' will be set to
    true.

    Finally, any housework tasks are excluded from being cleared, since these don't occur on daily
    intervals, so you generally don't want to reset these tasks to the current day. If the `--today`
    flag hasn't been used they'll be cleared out anyway. The reason for this check is because the
    housework project is under the routine parent project and I still want to keep it there, but it
    needs to be treated slightly differently from the daily routine projects.
    """
    for task in tasks:
        if task['project_id'] == HOUSEWORK_PROJECT_ID and use_today:
            continue
        print('Clearing current due date on "{}" if applicable'.format(task['content']))
        item = api.items.get_by_id(task['id'])
        due = item['due']
        due['date'] = datetime.strftime(datetime.now(), "%Y-%m-%d") if use_today else None
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
    work_tasks = get_due_or_overdue_tasks(api, ACTIVE_PERSONAL_PROJECTS_ID)
    clear_due_dates(api, work_tasks)
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
