from heuristics import Defender
from nodes import *
import json
import ast
import sys
import os


def read_tree(pycode: bytes):
    parsed = {'imports': [], 'functions': [], 'classes': [], 'libraries': [], 'if_main': [],'warnings': []}
    try:
        tree = ast.parse(pycode)
    except:
        return parsed
    body = tree.body
    for element in body:
        # check for import statements
        if type(element) == ast.Import:
            parsed['imports'].append(parse_import(element))
            for lib in element.names:
                parsed['libraries'].append(lib.name)
        # check for individual module imports
        elif type(element) == ast.ImportFrom:
            parsed['imports'].append(parse_import_from(element))
            parsed['libraries'].append(element.module)
        # check for function definitions
        elif type(element) == ast.FunctionDef:
            fsig, data = parse_function_def(element)
            parsed['functions'].append(fsig)
            # TODO: feed content of code in data variable to heuristics
        # check for class definitions
        elif type(element) == ast.ClassDef:
            csig, data = explore_class(element)
            # TODO: feed content of code in data variable to heuristics
            parsed['classes'].append(csig)
        # look for conditionals (will likely be __name__ == '__main__' at this level)
        elif type(element) == ast.If:
            parsed['if_main'].append(parse_if_main(element))
    return parsed


def explore_class(c: ast.ClassDef):
    data = {'name': c.name, 'functions': []}
    content = {}
    for node in c.body:
        # look for function definitions
        if type(node) == ast.FunctionDef:
            fsig, lines = parse_function_def(node)
            content[fsig] = lines
            data['functions'].append(str(fsig))
    return data, content


def process_file(filepath: str, config: dict, save: bool):
    # make sure file exists
    if not os.path.isfile(filepath):
        print(f'[X] Cannot find {filepath}')
        return []
    # Read in file
    code = open(filepath, 'rb').read()
    # parse and show the summary of the code
    tree = read_tree(code)
    tree['warnings'] = Defender(tree, config).warnings
    filename = f"{filepath.split('/')[-1].split('.')[0]}_summary.json"
    if save:
        # dump results
        open(filename, 'w').write((json.dumps(tree, indent=2)))
    # show warnings
    if len(tree['warnings'])>1:
        for warning in tree['warnings']:
            print(f'[{filepath}]: {warning}')
    return tree, filename


if __name__ == '__main__':
    if len(sys.argv) < 2:
        file_in = 'definitely_malicious.py'
        # from test_case import *
        # test_case.FakeDataGenerator('testData')
        code = open(file_in, 'rb').read()
    elif sys.argv[1].split('.')[-1] != 'py':
        print('[!] Please give lumberjack a python file :(')
        exit()
    else:
        file_in = sys.argv[1]
        code = open(file_in, 'rb').read()
    # parse and show the summary of the code
    tree = read_tree(code)
    for warning in Defender(tree,{}).warnings:
        tree['warnings'].append(warning)
    # dump results
    filename = f"{file_in.split('.')[0]}_summary.json"
    if len(tree['warnings']):
        for warning in tree['warnings']:
            print(f'[{file_in}]: {warning}')
    open(filename, 'w').write((json.dumps(tree, indent=1)))
