import test_case
from nodes import *
import json
import ast
import sys
import os


def read_tree(pycode: str):
    parsed = {'imports': [], 'functions': [], 'classes': []}
    tree = ast.parse(pycode)
    body = tree.body
    for element in body:
        # check for import statements
        if type(element) == ast.Import:
            parsed['imports'].append(element.names[0].name)

        # check for individual module imports
        elif type(element) == ast.ImportFrom:
            m = element.module
            for lib in element.names:
                parsed['imports'].append('.'.join([m, lib.name]))

        # check for function definitions
        elif type(element) == ast.FunctionDef:
            parsed['functions'].append(parse_function_def(element))

        # check for class definitions
        elif type(element) == ast.ClassDef:
            parsed['classes'].append(explore_class(element))
        # TODO: look for conditionals (will likely be __name__ == '__main__' at this level)
    return parsed


def explore_class(c: ast.ClassDef):
    data = {'name': c.name, 'functions': []}
    for node in c.body:
        # look for function definitions
        if type(node) == ast.FunctionDef:
            data['functions'].append(str(parse_function_def(node)))
    return data


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # from test_case import *
        # test_case.FakeDataGenerator('testData')
        code = open('test_case.py', 'rb').read()
    elif sys.argv[1].split('.')[-1] != 'py':
        print('[!] Please give lumberjack a python file :(')
        exit()
    else:
        code = open(sys.argv[1],'rb').read()
    # parse and show the summary of the code
    print(json.dumps(read_tree(code), indent=2))


