

class Defender:
    def __init__(self, summary: dict, config: dict):
        # Read Config
        self.sus, self.rules = self.setup(config)
        self.warnings = self.read_libraries(summary['imports'])
        for warning in self.read_functions(summary['functions']):
            self.warnings.append(warning)
        if len(summary['classes']):
            for c in summary['classes']:
                for warning in self.read_functions(c['functions']):
                    self.warnings.append(warning)

    def read_libraries(self, libs):
        flags = []
        for statement in libs:
            if type(statement) == list:
                for library in statement:
                    for blocked in self.sus:
                        if library.find(blocked) > -1:
                            flags.append(f'[!] potentially dangerous library {statement}')
            elif type(statement) == str:
                for library in self.sus:
                    if statement.find(library)>-1:
                        flags.append(f'[!] potentially dangerous library {statement}')
        return flags

    def read_functions(self, funcs):
        flags = []
        # sus = ['exec', 'Popen', 'encrypt', 'listen']
        for function_handle in funcs:
            fcn = function_handle.split('(')[0].lower()
            if fcn in self.rules:
                flags.append(f'[!] potentially dangerous function call: {function_handle}')
        return flags

    def setup(self, conf):
        libs = []
        bad_calls = []
        blocked = {0: ['delete', 'os.remove'],
                   1: ['encrypt', 'encrypt_file', 'encryptfile','encrypt_data'],
                   2: ['connect', 'listen', 'send', 'receive']}
        if 'libraries' in conf.keys():
            libs = conf['libraries']
        # TODO: Check rules
        if 'rules' in conf.keys():
            for n in conf['rules']:
                if n in blocked:
                    for values in blocked[n]:
                        bad_calls.append(values)
        return libs, bad_calls
