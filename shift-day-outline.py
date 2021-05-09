#!/usr/bin/env python

import os
import sys

from collections import namedtuple
from datetime import datetime, timedelta

from parse import parse
from todoist.api import TodoistAPI

from dev.tasks import create_jira_admin_task
from dev.tasks import create_merge_subtask
from dev.tasks import create_subtask
from dev.tasks import create_subtasks_from_file
from dev.ui import ui_create_root_task
from dev.ui import ui_create_subtasks
from dev.ui import ui_create_subtasks_from_file
from dev.ui import ui_get_jira_reference
from dev.ui import ui_get_main_repo
from projects import ui_select_work_project

DAY_OUTLINE_PROJECT_ID = 2235770611
Task = namedtuple('Task', ['id', 'name', 'due'])

api_token = os.getenv('TODOIST_API_TOKEN')
api = TodoistAPI(api_token)
api.sync()

class OutlineOverflowException(Exception):
    def __init__(self, message):
        super().__init__(message)

def get_new_day_outline_start_time():
    """
    Gets the new start time for the day outline. It will be rounded off to the nearest
    half hour. So if it's currently 1615, the new start time will be 1630. If it's 1645,
    the new start time will be 1700, and so on.
    """
    minutes_to_add = 0
    now = datetime.now()
    current_minute = now.minute
    if current_minute < 30:
        minutes_to_add = 30 - current_minute
    else:
        minutes_to_add = 60 - current_minute
    now_sans_seconds = datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute)
    return now_sans_seconds + timedelta(minutes=minutes_to_add)

def parse_duration_from_task(task):
    """
    The duration part of the outline tasks will be defined by me and they will always be
    defined as "X hour(s)", where X will be a decimal. However, if there's a fractional
    part of the decimal, it will *always* be .5, because I will only do these blocks of
    time in increments of 30 minutes.

    The duration that will be returned here will be in minutes.
    """
    result = parse('{} [{}]', task.name)
    hours = result[1].split(' ')[0]
    if '.' in hours:
        hour = hours.split('.')[0]
        return (int(hour) * 60) + 30
    return int(hours) * 60

def get_new_due_date_for_task(start_time, task_duration):
    if start_time.day > datetime.now().day:
        raise OutlineOverflowException(
            'The new start time overflows to the next day. Please adjust the duration of the task.'
        )
    return start_time + timedelta(minutes=task_duration)

def get_outline_tasks_for_today():
    day_outline_project = api.projects.get_data(DAY_OUTLINE_PROJECT_ID)
    tasks_with_due_dates = [
        Task(x['id'], x['content'], datetime.strptime(x['due']['date'], '%Y-%m-%dT%H:%M:%S'))
        for x in day_outline_project['items'] if x['due']
    ]
    return sorted(
        [x for x in tasks_with_due_dates if x.due.date() == datetime.now().date()],
        key = lambda x: x.due)

def get_current_day_outline_tasks():
    current_day_outline_tasks = get_outline_tasks_for_today()
    new_outline_start_time = get_new_day_outline_start_time()
    if new_outline_start_time.day > datetime.now().day:
        raise OutlineOverflowException('The new outline start time overflows to the next day.')
    return current_day_outline_tasks

def build_shifted_outline(current_day_outline_tasks):
    shifted_tasks = [Task(
        current_day_outline_tasks[0].id,
        current_day_outline_tasks[0].name,
        get_new_day_outline_start_time())]
    i = 1
    while i < len(current_day_outline_tasks):
        task = current_day_outline_tasks[i]
        duration = parse_duration_from_task(current_day_outline_tasks[i - 1])
        start_time = get_new_due_date_for_task(shifted_tasks[i - 1].due, duration)
        shifted_tasks.append(Task(task.id, task.name, start_time))
        i += 1
    return shifted_tasks

def main():
    try:
        current_day_outline_tasks = get_current_day_outline_tasks()
        shifted_tasks = build_shifted_outline(current_day_outline_tasks)
        for task in shifted_tasks:
            item = api.items.get_by_id(task.id)
            item.update(
                due={ 'date': datetime.strftime(task.due, '%Y-%m-%dT%H:%M:%S') })
        api.commit()
        return 0
    except OutlineOverflowException as e:
        print(e)
        return 1

if __name__ == '__main__':
    sys.exit(main())
