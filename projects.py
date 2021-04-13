WORK_PARENT_PROJECT_ID = 2235604758

def ui_select_work_project(api):
    projects = {
        p['name']:p['id']
        for p in api.state['projects'] if p['parent_id'] == WORK_PARENT_PROJECT_ID
    }
    count = 1
    sorted_project_names = sorted(projects.keys())
    for project in sorted_project_names:
        print("{num}. {project_name}".format(num=count, project_name=project))
        count += 1
    selected_project_name = get_valid_project_selection(sorted_project_names)
    print("Working with project {project}".format(project=selected_project_name))
    print()
    return (selected_project_name, projects[selected_project_name])

def get_project_id(api, name):
    projects = { p['name']:p['id'] for p in api.state['projects'] }
    id = projects.get(name)
    if not id:
        raise ValueError("The project {} doesn't exist".format(name))
    return id

def get_valid_project_selection(projects):
    print("Please select the project to work with: ")
    while True:
        selection = input(">> ")
        try:
            numeric_selection = int(selection)
            if numeric_selection < 1 or numeric_selection > len(projects):
                print("Please enter a value between 1 and {0}.".format(len(projects)))
                continue
            return projects[numeric_selection - 1]
        except ValueError:
            print("Please enter a value between 1 and {}.".format(len(projects)))
