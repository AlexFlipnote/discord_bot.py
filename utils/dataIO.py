import json


def change_value(file, value, changeto):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value] = changeto
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)


def append_value(file, value, addition):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value].append(addition)
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)
