import ast


def parse_args(node: ast.arguments):
    results = []
    for a in node.args:
        fields = a._fields
        if 'annotation' in fields and a.annotation != None:
            results.append(f'{a.arg}:{a.annotation.id}')
        else:
            results.append(a.arg)
    return results


def parse_function_def(f:ast.FunctionDef):
    args = parse_args(f.args)
    fcn = f'{f.name}({",".join(args)})'
    # TODO: parse body
    return fcn


def parse_import(i:ast.Import):
    imp = f''
    for lib in i.names:
        imp += f'import {lib.name}'
    return imp

# TODO: Generic parsing of node types:
def walk_node(node):
    data = {'name': '', 'args': '','actions': [], 'type':''}
    types = {ast.Import: 'import', ast.ImportFrom: 'import from',
             ast.Call: ''}
    if type(node) in types.keys():
        data['type'] = types[type(node)]
    for branch in ast.walk(node):
        fields = branch._fields
        if 'func' in fields:
            data['actions'].append(branch.func.id)
        if 'name' in fields:
            data['name'] = branch.name
        if 'args' in fields:
            data['args'] = parse_args(branch)
        if 'value' in fields:
            if type(branch.value) == ast.Constant:
                data['val'] = branch.value.value
            else:
                data['val'] = branch.value.id
    return data




