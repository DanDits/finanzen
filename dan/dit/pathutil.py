import os
import sys

def project_dir():
    curr_path = os.path.realpath(__file__)
    parent_dir = os.path.dirname(curr_path)
    parent_dir = os.path.dirname(parent_dir)
    parent_dir = os.path.dirname(parent_dir)
    return parent_dir


def umsatz_dir():
    if sys.argv and len(sys.argv) > 1:
        given_path = "data/" + sys.argv[1]
    else:
        given_path = "data/umsatz"
    return os.path.join(project_dir(), given_path)


def umsatz_file(file_name):
    return os.path.join(umsatz_dir(), file_name)
