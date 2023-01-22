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


if __name__ == '__main__':
    print(json.dumps(crawl_dir(os.getcwd(), {}, True)))

