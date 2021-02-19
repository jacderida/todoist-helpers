def ui_get_user_project_selection(api):
    projects = { p['name']:p['id'] for p in api.state['projects'] }
    count = 1
    sorted_project_names = sorted(projects.keys())
    for project in sorted_project_names:
        print("{num}. {project_name}".format(num=count, project_name=project))
        count += 1
    selected_project_name = get_valid_project_selection(sorted_project_names)
    return (selected_project_name, projects[selected_project_name])

def get_valid_project_selection(projects):
    print("Please select the project to work with: ")
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
