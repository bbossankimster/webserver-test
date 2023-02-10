import json


def read_json(file):
    data_dict = {}
    with open(file, "r") as f:
        data_dict = json.load(f)
    return data_dict


def write_json(file, result_dict):
    with open(file, "w") as f:
        f.writelines(json.dumps(result_dict, indent=3))
