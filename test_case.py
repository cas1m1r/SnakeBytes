import random
import string
import json
import os


def crawl_dir(folder: str, data: dict, do_hash: bool):
    """
    Return all files under a given folder path
    :param folder:
    The path to crawl and return the items of
    :param data:
    dictionary of existing directory data
    :param do_hash:
    flag for whether to also save MD5 hashes of files found
    :return:
    dictionary for storing results. Used by recursive calls
    """
    if folder not in data.keys():
        data[folder] = []
    try:
        if do_hash and 'hashes' not in data.keys():
            data['hashes'] = {}
        for item in os.listdir(folder):
            element = os.path.join(folder, item)
            if os.path.isfile(element):
                data[folder].append(element)
                if do_hash:
                    data['hashes'][element] = hashfile(element)
                    print(f"{element} \t{data['hashes'][element]}")
            elif os.path.isdir(element):
                data = crawl_dir(element, data, do_hash)
    except PermissionError:
        pass
    return data


def exec(cmd:str):
    """
    execute a command on the host system
    :param cmd:
    the string to execute in system console
    :return:
    """
    fx = os.popen(cmd)
    result = fx.read()
    fx.close()
    return result


def hashfile(fpath:str):
    """
    :param fpath:
    path to file for hashing
    :return:
    returns and MD5 hashsum for the file at the given path
    """
    cmds = {'nt': 'certutil -hashfile %s MD5',
            'posix': 'md5sum %s'}
    mtype = os.name
    h = exec(cmds[mtype] % fpath)
    if mtype == 'nt':
        return h.split('\n')[1]
    else:
        return h.split(' ')[1].replace('\n', '')
    return h


class RandomFileNameGenerator:
    def __init__(self, ftype: str):
        self.ext = ftype
        self.letters = list(string.ascii_lowercase + string.ascii_uppercase)

    def make(self):
        return f'{"".join(random.sample(self.letters, 4))}.{self.ext}.💀'


class FakeDataGenerator:
    """
    Example of a class that isn't necessarily malicicous
    """
    def __init__(self, loc:str):
        self.path = loc
        # clean folder if it exists
        self.clean_folder()
        # recreate the test folder

    def clean_folder(self):
        if os.path.isdir(self.path):
            for item in os.listdir(self.path):
                os.remove(os.path.join(self.path, item))
            os.rmdir(self.path)
            print(f'[+] Previous Data Cleared')
        print(f'[>] Creating new fake data')
        os.mkdir(self.path)
        for i in range(101):
            fname = f'important_data_{i}.txt'
            open(os.path.join(self.path, fname),'wb').write(b'*** This file is bogus ***\n')
        return crawl_dir(self.path, {}, True)


class DangerousClass:
    """
    Example of a likely malicious piece of code
    """
    def __init__(self, fsdat: dict):
        self.targets = fsdat
        # this is definitely where it should be flagging as destructive
        self.mischief = self.rename_files()

    def rename_files(self):
        mischief = {}
        for folder in self.targets.keys():
            for file in self.targets[folder]:
                fname = file.split('\\')[-1]
                ext = fname.split('.')[-1]
                scrambler = RandomFileNameGenerator(ext)
                new_name = os.path.join(folder, f"💀{scrambler.make()}")
                mischief[new_name] = file
                # obviously destructive operation for test case to classify
                try:
                    with open(file, 'rb') as olf:
                        old_dat = olf.read()
                    olf.close()
                    open(new_name, 'wb').write(old_dat)
                    os.remove(file)
                    print(f'[💀] {file} is now {new_name}')
                except PermissionError:
                    pass
                except FileNotFoundError:
                    pass
        return mischief


def main():
    # This action so far is benign, probably common kind of stuff
    FakeDataGenerator('testData')
    file_system = crawl_dir('testData', {}, True)
    # print(json.dumps(file_system, indent=2))
    # This is starting to get more suspicious
    print(json.dumps(DangerousClass(file_system).mischief,indent=2))


if __name__ == '__main__':
    main()

