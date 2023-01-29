import ast


def parse_args(node: ast.arguments):
    results = []
    for a in node.args:
        fields = a._fields
        if 'annotation' in fields and type(a.annotation) != None:
            try:
                results.append(f'{a.arg}: {a.annotation.id}')
            except AttributeError:
                # print(f'{a}:\t1{a.annotation}')
                pass
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
               ast.For: parse_for_loop, ast.Assign: expand_assignment,
               ast.Expr: expand_expr}
    for node in body:
        T = type(node)
        if T in actions.keys():
            elements.append(actions[T](node))
    return elements


def parse_function_def(f:ast.FunctionDef):
    args = parse_args(f.args)
    fcn = f'{f.name}({", ".join(args)})'
    body = expand_body(f.body)
    return fcn, body


def parse_import(i: ast.Import):
    imps = []
    if len(i.names) > 1:
        for lib in i.names:
            imps.append(lib.name)
        return imps
    else:
        return i.names[0].name


def parse_import_from(i:ast.ImportFrom):
    m = i.module
    imports = []
    for lib in i.names:
        try:
            imports.append('.'.join([m, lib.name]))
        except TypeError:
            imports.append(lib.name)
            pass
    return imports


def parse_if_main(i: ast.If):
    # TODO: verify this is an if '__name__' == '__main__' statement
    routine = {'body': expand_body(i.body)}
    return routine


def parse_if(node: ast.If):
    ops = {ast.In: ' in ', ast.NotIn: ' not in ', ast.Eq: ' == ', ast.NotEq: ' != ',
           ast.And: ' and ', ast.Gt: '>', ast.Lt: '<', ast.GtE: '>=', ast.LtE: '<='}
    data = {'statement': '', 'body': []}
    try:
        if 'left' in node.test._fields:
            lhs = node.test.left
            if 'id' in lhs._fields:
                LHS = lhs.id
            elif type(lhs) == ast.Call:
                LHS = unpack_attribute(lhs)
            elif type(lhs) == ast.Name:
                LHS = lhs.id
            elif type(lhs) == ast.Attribute:
                LHS = unpack_attribute(lhs)
            elif type(lhs) == ast.Compare:
                LHS = lhs.value
            elif type(lhs) == ast.Constant:
                LHS = lhs.value
            test = ''
            for v in node.test.ops:
                t = type(v)
                if t in ops.keys():
                    test += ops[t]
            for op in node.test.comparators:
                T = type(op)
                if T == ast.Call:
                    rhs = f'{unpack_attribute(op.func)}({unpack_attribute(op.args[0])})'
                    data['statement'] = f'if {LHS} {test} {rhs}'
                else:
                    rhs = ''
                    for r in node.test.comparators:
                        # if 'value' in r._fields:
                        #     rhs += f'{r.value}'
                        if type(r) == ast.Call:
                            rhs += unpack_attribute(r)
                    data['statement'] = f'if {LHS} {test} {rhs}'

                # else:
                #     print(f'Havent created if {T}')
        elif type(node.test) != ast.Call and 'op' in node.test._fields and type(node.test.op) in ops.keys():
            data['statement'] = ops[type(node.test.op)]


    except AttributeError:
        pass
    # TODO PARSE BODY
    data['body'] = parse_body(node.body)
    return data


def expand_body(body:list):
    data = {'code': []}
    actions = {ast.arguments: parse_args, ast.FunctionDef: parse_function_def,
               ast.Import: parse_import, ast.ImportFrom: parse_import_from,
               ast.Expr: expand_expr, ast.If: parse_if, ast.Try: expand_try,
               ast.For: parse_for_loop, ast.Assign: expand_assignment}
    for node in body:
        T = type(node)
        if T in actions.keys():
            data['code'].append(actions[T](node))
        # else:
        #     print(f'No Method for {T}')
    # TODO: Its bad syntax but people could include import statements elsewhere!
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
    try:
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
    except AttributeError:
        pass
    return data


def unpack_attribute(a : ast.Attribute):
    attr = []
    for level in ast.walk(a):
            items = level._fields
            if 'attr' in items:
                attr.append(f'{level.attr}')
            elif 'id' in items:
                attr.append(f'{level.id}')
            elif 'value' in items:
                attr.append(f'{level.value}')
    attr.reverse()
    return '.'.join(attr)


def expand_assignment(a: ast.Assign):
    expr = ''
    lhs = []
    rhs = []
    for node in ast.walk(a):
        items = node._fields
        if 'id' in items:
            rhs.append(node.id)
        if 'targets' in items:
            if 'args' in items:
                rhs.append(parse_args(node))
            if 'attr' in node._fields:
                rhs.append(node.target.attr)
            if 'id' in items:
                rhs.append(node.target.id)
            for target in node.targets:
                if type(target) == ast.Name:
                    lhs.append(f'{target.id}')
        if 'value' in items:
            if type(node.value) == ast.Call:
                if 'func' in node.value._fields:
                    rhs.append(f'{unpack_attribute(node.value)}('.replace('. ',''))
                for arg in node.value.args:
                    rhs.append(f'{unpack_attribute(arg)}')
                rhs.append(')')
            elif type(node.value) == ast.Constant:
                rhs.append(f'{node.value.value}')
    return f'{" ".join(lhs)} = {"".join(rhs)}'

