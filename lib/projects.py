def get_project_id(api, name):
    projects = { p['name']:p['id'] for p in api.state['projects'] }
    id = projects.get(name)
    if not id:
        raise ValueError("The project {} doesn't exist".format(name))
    return id

def get_valid_project_selection(projects):
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
