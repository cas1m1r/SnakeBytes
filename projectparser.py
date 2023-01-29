from utils import *
import heuristics
import lumberjack
import json
import sys
import os


def is_py_file(fname):
    ext = fname.split('.')[-1]
    return ext == 'py'


def find_python_files(folder: str, data: list):
    for item in os.listdir(folder):
        fpath = os.path.join(folder, item)
        if os.path.isfile(fpath) and fpath not in data and is_py_file(fpath):
            data.append(fpath)
        elif os.path.isdir(fpath):
            data = find_python_files(fpath, data)
    return data


def create_security_config():
    libraries = []
    heuristic_opts = []
    adding_libraries = True
    adding_heuristics = True
    while adding_libraries:
        try:
            blocked = input('Enter name of library to look in imports [q to quit]:')
            if blocked.lower() == 'q':
                adding_libraries = False
            else:
                libraries.append(blocked)
        except KeyboardInterrupt:
            adding_libraries = False
            pass

    print(f'Thanks! Now Select Security Rules to look for in python code [enter q to quit]:')
    options = {0: 'File Deletion',
               1: 'File Encryption',
               2: 'Telemetry/Data Ex-filtration'}
    for n in range(0, len(options.keys())):
        print(f'Do you want to flag python code that attempts {options[n]}')
        try:
            choice = input('Enter Y/N: ').upper()
            if choice == 'Y':
                heuristic_opts.append(n)
            elif choice == 'N':
                print('Okay, all set.')
        except KeyboardInterrupt:
            break
            pass
    return {'libraries': libraries, 'rules': heuristic_opts}


def check_for_config():
    for fname in os.listdir(os.getcwd()):
        if fname == 'security_config.json':
            print(f'[+] Found Security Config')
            return json.loads(open('security_config.json','r').read())
    print(f'[!] No security config found')
    return {}


def usage():
    print(f'Usage: python {sys.argv[0]} [path-to-python-project]')
    exit()


def main():
    # Find Configuration for rules to apply
    conf = check_for_config()
    if conf == {}:
        conf = create_security_config()
        open('security_config.json', 'w').write(json.dumps(conf))
    # Check for Project Location Input
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        usage()
    # make sure project path exists
    if not os.path.isdir(project_path):
        print(f'Cannot find {project_path}')
    # Find all python files in the project
    py_files = find_python_files(project_path, [])
    # traverse every tree of any python file found with lumberjack
    for pyfile in py_files:
        summary, outputfile = lumberjack.process_file(pyfile, conf, False)
        # check if any rules are violated
        rules = heuristics.Defender(summary, conf)
        if len(rules.warnings):
            for violation in rules.warnings:
                print(violation)


if __name__ == '__main__':
    main()
