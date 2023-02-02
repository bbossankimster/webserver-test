import pickle


def read_file(file):
    with open(file, 'rb') as f:
        content = pickle.load(f)
    return content


def write_file(file, content):
    with open(file, 'wb') as f:
        pickle.dump(content, f)
