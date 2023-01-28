import ast


def parse_args(node: ast.arguments):
    results = []
    for a in node.args:
        fields = a._fields
        if 'annotation' in fields and a.annotation != None:
            results.append(f'{a.arg}: {a.annotation.id}')
        elif 'arg' in fields:
            results.append(a.arg)
        elif 'id' in fields:
            results.append(a.id)
        else:
            results.append(a.value)
    return results


def parse_body(body: list):
    elements = []
    actions = {ast.arguments: parse_args, ast.FunctionDef: parse_function_def,
               ast.Import: parse_import, ast.ImportFrom: parse_import_from,
               ast.For: parse_for_loop}
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
    body = expand_body(f.body)
    return fcn, body


def parse_import(i: ast.Import):
    imps = []
    for lib in i.names:
        imps.append(lib.name)
    return imps


def parse_import_from(i:ast.ImportFrom):
    m = i.module
    imports = []
    for lib in i.names:
        imports.append(lib.name)
    return [m, imports]


def parse_if_main(i: ast.If):
    # TODO: verify this is an if '__name__' == '__main__' statement
    routine = {'body': expand_body(i.body)}
    return routine


def parse_if(node: ast.If):
    ops = {ast.In: ' in ', ast.NotIn: ' not in ', ast.Eq: ' == ', ast.NotEq: ' != ',
           ast.And: ' and '}
    data = ''
    if 'left' in node.test._fields:
        lhs = node.test.left
        test = ''
        for v in node.test.ops:
            t = type(v)
            if t in ops.keys():
                test += ops[t]
        for op in node.test.comparators:
            T = type(op)
            if T == ast.Call:
                rhs = '.'.join([op.func.value.id, op.func.attr])
                data = f'if {lhs.id} {test} {rhs}()'
            else:
                print(f'Havent created if {T}')
    elif type(node.test) != ast.Call and type(node.test.op) in ops.keys():
        data = ops[type(node.test.op)]
    return data


def expand_body(body:list):
    data = {'code': []}
    actions = {ast.arguments: parse_args, ast.FunctionDef: parse_function_def,
               ast.Import: parse_import, ast.ImportFrom: parse_import_from,
               ast.Expr: expand_expr, ast.If: parse_if, ast.Try: expand_try,
               ast.For: parse_for_loop}
    for node in body:
        T = type(node)
        if T in actions.keys():
            data['code'].append(actions[T](node))
        else:
            print(f'No Method for {T}')
    return data


def expand_expr(e: ast.Expr):
    if 'value' in e.value._fields:
        return e.value.value


def expand_try(t: ast.Try):
    data = {'try': expand_body(t.body),
            'catch': expand_body(t.handlers)}
    return data


def parse_for_loop(f: ast.For):
    data = {}
    loopvar = f.target.id
    iterable = f.iter
    data['loop_element'] = loopvar
    # parse the iterable portion of forloop
    if type(f.iter) == ast.Call:
        if 'attr' in f.iter.func._fields and 'id' in f.iter.func.value._fields:
            able = f'{".".join([f.iter.func.value.id, f.iter.func.attr])}('
        elif type(f.iter.func) == ast.Attribute:
            able = f'{unpack_attribute(f.iter.func)}('
        else:
            able = f'{f.iter.func.id}('
        data['iterable'] = able
        for arg in f.iter.args:
            if type(arg) == ast.Constant:
                data['iterable'] = f'{arg.value}'
            elif 'attr' in arg._fields:
                data['iterable'] += f'{arg.attr}, '
            elif type(arg) == ast.Call:
                data['iterable'] += f'{parse_args(arg)}, '
        data['iterable'] += ')'
    return data


def unpack_attribute(a : ast.Attribute):
    attr = []
    for level in ast.walk(a):
            items = level._fields
            if 'attr' in items:
                attr.append(level.attr)
            elif 'id' in items:
                attr.append(level.id)
    attr.reverse()
    return '.'.join(attr)
