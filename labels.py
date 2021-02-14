import sys

def get_label_ids(api, labels):
    label_ids = []
    for label in labels:
        try:
            retrieved_label = next(x for x in api.state['labels'] if label in x['name'])
            label_ids.append(retrieved_label['id'])
        except StopIteration:
            print("Label '{label}' doesn't exist. Please respecify with a valid label.".format(
                label=label))
            sys.exit(1)
    return label_ids
