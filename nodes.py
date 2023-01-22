import ast


class Expression:
    def __init__(self, element):
        self.style = type(element)


class Conditional:
    def __init__(self, element):
        self.lhs = self.get_lhs(element)
        self.rhs = self.get_rgs(element)

    def get_lhs(self, node):
        if type(node) == ast.If:
            return node.test.left.id
        else:
            print(f'[!] Element given is not an IF Statement')
            return []


    def get_rhs(self, node):
        if type(node) == ast.If:
            return node.test.right


class Function:
    def __init__(self, element):
        self.handle = element.name
        self.output = element.returns
        self.arguments = self.parse_args(element)
        self.lhs_items, self.rhs_items = self.parse_body(element)

    def parse_args(self, node: ast.FunctionDef):
        args = {}
        for arg in node.args.args:
            try:
                args[arg.arg] = arg.annotation.id
            except AttributeError:
                pass
        return args

    def parse_body(self, node: ast.FunctionDef):
        lhs = []
        rhs = []
        for element in node.body:
            if type(element) == ast.Assign:
                for l in element.targets:
                    if 'id' in l._fields:
                        lhs.append(l.id)
                r = element.value
                # check if rhs is a f()
                if type(r) == ast.Call:
                    fs = r.func._fields
                    try:
                        f = {'args': [a.id for a in r.args],
                             'fcn' : []}
                    except AttributeError:
                        f = {}
                        pass
                    if 'attr' in fs:
                        f['fcn'].append(r.func.attr)
                    if 'value' in fs:
                        f['fcn'].append(r.func.value)
                    rhs.append(f)
        return lhs, rhs

    def json(self):
        content = {'name': self.handle,
                   'inputs': self.arguments,
                   }
        return content

    def __str__(self):
        return f"{self.handle}({', '.join(self.arguments.keys())})"
