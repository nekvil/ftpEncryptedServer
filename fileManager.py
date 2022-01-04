import os
import re
import configparser
from sys import platform
from pathlib import Path
from shutil import copyfile
from datetime import datetime
from colorama import init


def cat(name_file):
    msg = ""
    i = 0
    if os.path.exists(name_file) and os.path.isfile(name_file):
        file = open(name_file, 'r')
        try:
            lines = file.readlines()
            for line in lines:
                if i == len(lines) - 1:
                    msg += line.strip()
                else:
                    msg += line.strip() + "\n"
                i += 1
        finally:
            file.close()
    else:
        msg += "\033[31m" + 'No such file' + '\033[0m'
    return msg


def ls(path):
    with os.scandir(path) as it:
        msg = (f'{"Name":<20}'
               # f'{"Path":<30}'
               f'{"Size":>10}'
               f'{"Type":>15}'
               f'{"Modified":>21}'
               )
        msg += "\n"
        msg += (66 * "-")
        msg += "\n"

        for entry in it:

            size = 0
            as_str = ""

            if entry.is_file():
                typ = "File"
            else:
                typ = "Directory"

            if entry.stat().st_size > 1024:
                size = entry.stat().st_size / 1024
            else:
                size = entry.stat().st_size

            if int(size) == 0:
                as_str = ""
            else:
                as_str = str(int(size))

            msg += (f'{entry.name[:20]:<20}'
                    # f'{entry.path[:30]:<30}'
                    f'{as_str:>10}'
                    f'{typ:>15}'
                    f'{"":>5}'
                    f'{datetime.fromtimestamp(entry.stat().st_mtime):%d.%m.%Y %H:%M}'
                    "\n")
    return msg


def help_():
    return "ls - View a list of the files and folders in a given directory\n" + "wd - Display the current working " \
                                                                                "directory\n" + "crdir - Create a new "\
                                                                                                "directory\n" + \
           "dldir - Delete an empty directory\n" + "dl - Delete the file\n" + "cd - Change the current working " \
                                                                              "directory\n" + "create - Create a new " \
                                                                                              "file\n" + "read - Read "\
                                                                                                         "the file\n" \
           + "write - Write the file\n" + "rnm - Rename the file\n" + "rpl - Replace the file\n" + "copy - Copy the " \
                                                                                                   "file "


def mkdir(name_dir):
    if not os.path.exists(name_dir) and not os.path.isdir(name_dir):
        os.mkdir(name_dir)
        return ""
    else:
        return "\033[31m" + 'DirectoryExistsError' + '\033[0m'


def set_settings():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    os.chdir(config["Settings"]["home_dir"])


def create_config(path):
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "home_dir", str(Path.home()))

    with open(path, "w") as config_file:
        config.write(config_file)

    config_file.close()


def rmdir(name_dir):
    if os.path.exists(name_dir) and os.path.isdir(name_dir):
        os.rmdir(name_dir)
    else:
        return "\033[31m" + 'No such directory' + '\033[0m'
    return ""


def rename(name_file, new_name_file):
    if os.path.exists(name_file) and os.path.isfile(name_file):
        path = os.path.join(os.path.abspath(os.path.dirname(name_file)), name_file)
        new_path = os.path.join(os.path.abspath(os.path.dirname(name_file)), new_name_file)
        os.rename(path, new_path)
    else:
        return "\033[31m" + 'No such file' + '\033[0m'
    return ""


def replace(name_file, new_path):
    if os.path.exists(name_file) and os.path.isfile(name_file):
        path = os.path.join(os.path.abspath(os.path.dirname(name_file)), name_file)
        new_path = os.path.join(new_path, name_file)
        os.replace(path, new_path)
    else:
        return "\033[31m" + 'No such file' + '\033[0m'
    return ""


def cp(name_file, new_path, file_name):
    if os.path.exists(name_file) and os.path.isfile(name_file):
        path = os.path.join(os.path.abspath(os.path.dirname(name_file)), name_file)
        new_path = os.path.join(new_path, file_name)
        copyfile(path, new_path)
    else:
        return "\033[31m" + 'No such file' + '\033[0m'
    return ""


def write(name_file, info):
    if os.path.exists(name_file) and os.path.isfile(name_file):
        file = open(name_file, 'a')
        try:
            file.write(info + '\n')
        finally:
            file.close()
    else:
        return "\033[31m" + 'No such file' + '\033[0m'
    return ""


def rm(name_file):
    if os.path.exists(name_file) and os.path.isfile(name_file):
        os.remove(name_file)
    else:
        return "\033[31m" + 'No such file' + '\033[0m'
    return ""


def cd(name_dir, home_dir):
    # config = configparser.ConfigParser()
    # config.read(os.path.join(path_to_config, 'settings.ini'))
    dir_ = os.path.join(os.getcwd(), home_dir, name_dir)

    if os.path.exists(dir_) and os.path.isdir(dir_):
        # linux exception config !
        if os.getcwd() == os.path.join(os.getcwd(), home_dir) and name_dir == "..":
            return ""
        else:
            return os.path.join(home_dir, name_dir)
    else:
        return "\033[31m" + 'No such directory' + '\033[0m'


def pwd():
    return os.getcwd()


# Cross-Platform chars in dir name
def check_dir_name(name_dir):
    exception_chars = ""
    os_type = check_os()

    if os_type == "win":
        exception_chars = '\\\/\|<>\?:"\*'
    elif os_type == "linux":
        exception_chars = '\\\/\|<>\?:"\*'
    find_exceptions = re.compile('([{}])'.format(exception_chars))
    res = find_exceptions.findall(name_dir)
    if res:
        print('Name "{}" contains except chars: {}'.format(name_dir, res))
        return False
    else:
        return name_dir


def check_os():
    if platform == "linux" or platform == "linux2":
        return "linux"
    # elif platform == "darwin":
    #     macOS = True
    elif platform == "win32":
        return "win"


def touch(name_file):
    if not os.path.exists(name_file) and not os.path.isfile(name_file):
        file = open(name_file, "w")
        file.close()
    else:
        return "\033[31m" + 'FileExistsError' + '\033[0m'
    return ""


init()
