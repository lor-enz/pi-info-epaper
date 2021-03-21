
#    stores data in human readable file
#    overwrites all previous data of file
def store(filename, data):
    import json
    with open(ensure_dot_json(filename), 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)


def retrieve(filename):
    import json
    with open(ensure_dot_json(filename), 'r') as fp:
        return json.load(fp)


def ensure_dot_json(filename):
    if filename.endswith('.json'):
        return filename
    return f'{filename}.json'
