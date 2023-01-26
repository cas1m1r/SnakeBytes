import ast


def parse_args(node: ast.arguments):
    results = []
    for a in node.args:
        fields = a._fields
        if 'annotation' in fields and a.annotation != None:
            results.append(f'{a.arg}: {a.annotation.id}')
        else:
            results.append(a.arg)
    return results


def parse_body(body: list):
    elements = []
    actions = {ast.arguments: parse_args, ast.FunctionDef: parse_function_def,
               ast.Import: parse_import, ast.ImportFrom: parse_import_from}
    for node in body:
        T = type(node)
        if T not in actions.keys():
            print(f'Unknown type {T}')
        else:
            elements.append(actions[T](node))
    return elements


def parse_function_def(f:ast.FunctionDef):
    args = parse_args(f.args)
    fcn = f'{f.name}({", ".join(args)})'
    # TODO: parse body
    return fcn


def parse_import(i: ast.Import):
    imp = f''
    for lib in i.names:
        imp += f'import {lib.name}'
    return imp


def parse_import_from(i:ast.ImportFrom):
    m = i.module
    imports = []
    for lib in i.names:
        imports.append(lib.name)
    return f'from {m} import {",".join(imports)}'


def parse_if_main(i: ast.If):
    # TODO: verify this is an if '__name__' == '__main__' statement
    routine = {'body': parse_body(i.body)}
    # TODO: determine entry point to main
    return routine



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




