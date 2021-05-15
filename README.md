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

For work tasks that involve supplying a JIRA reference, you should set the `JIRA_BASE_URL` variable, which is the part of the URL that occurs before the reference to the ticket.
