# Todoist Helpers

Scripts for automating tedious things I do a lot with Todoist.

## Setup

To use with Fish, install [virtualfish](https://virtualfish.readthedocs.io/en/latest/install.html), then run the following commands:
```
vf new todoist
vf activate todoist
pip install -r requirements.txt
```

The `TODOIST_API_TOKEN` must be set to the API token for the account. The token can be retrieved by going to `Todoist Settings -> Integrations -> API token`.

## Scripts

### Add List of Tasks to a New Section

The `add-tasks-to-section.py` script will take a list of tasks that have been specified in a file and add them to a new section. There are 2 prompts: one to select the project to add the section to, and another to specify the name of the new section. The file that specifies the tasks to add must be supplied as an argument to the script. It can be a relative path.

The file should be in the following format:
```
MAP01: 100% playthrough; ['reward', 'games', 'home']
MAP01: 100% no saves playthrough; ['reward', 'games', 'home']
MAP01: 100% no saves demo; ['reward', 'games', 'home']
```

Where the `;` separates the name of the task and the list of labels to apply to it.

### Create Terraform Task

For development work, I like to have the main outcome of the work as the 'parent' task, with the subtasks being all the steps involved in completing the work. There are subtasks I wanted to have that I found myself creating all the time and that got pretty tedious, so I decided to automate it with this script.
