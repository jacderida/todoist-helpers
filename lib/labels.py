import sys

def get_full_label_name(api, name):
    return get_full_label_names(api, [name])[0]

def get_full_label_names(api, label_names):
    retrieved_labels = api.get_labels()
    full_label_names = []
    for label in label_names:
        try:
            if label == "work":
                label_name = [x.name for x in retrieved_labels if label in x.name][1]
            else:
                label_name = next(x.name for x in retrieved_labels if label in x.name)
            full_label_names.append(label_name)
        except StopIteration:
            print("Label '{label}' doesn't exist. Please respecify with a valid label.".format(
                label=label))
            sys.exit(1)
    return full_label_names
