# sorter.py
"""Sort files by extension. Can unpack supported archives."""
""" Default file processing settings:
    {
        "archives"  :   {
            "extensions"    :   ["zip", "tar", "tgz", "gz", "7zip", "7z", "iso", "rar"],
            "functions"     :   ["unpack","move"]
        },

        "video"     :   {
            "extensions"    :   ["avi", "mp4", "mov", "mkv"],
            "functions"     :   ["move"]
        },
        "audio"     :   {
            "extensions"    :   ["wav", "mp3", "ogg", "amr"],
            "functions"     :   ["move"]
        },
        "documents" :   {
            "extensions"    :   ["doc", "docx", "txt", "pdf", "xls", "xlsx", "ppt", "pptx", "rtf", "xml", "ini"],
            "functions"     :   ["move"]
        },
        "images"    :   {
            "extensions"    :   ["jpeg", "png", "jpg", "svg"],
            "functions"     :   ["move"]
        },
        "software"    :   {
            "extensions"    :   ["exe", "msi", "bat" , "dll"],
            "functions"     :   ["move"]
        },
        "other"     :   {
            "extensions"    :   [],
            "functions"     :   ["move"]
        }
    }
    Supported functions:
            #   copy, move, remove, unpack, delete(used for removing archives)
            #   order sensitive

TODO: 
    Refactory to use pathlib module
    add regexp to extensions processing
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from copy import deepcopy

args = None

def make_translate_table() -> dict:
    """Create translation table from cyrillic to latin. Also replace all other character with symbol - '_' except digits"""
    translation_table = {}
    latin = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
             "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

    # Make cyrillic tuplet
    cyrillic_symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    cyrillic_list = []
    for c in cyrillic_symbols:
        cyrillic_list.append(c)

    cyrillic = tuple(cyrillic_list)

    # Fill tranlation table
    for c, l in zip(cyrillic, latin):
        translation_table[ord(c)] = l
        translation_table[ord(c.upper())] = l.upper()

    # From symbol [NULL] to '/'. See ASCI table for more details.
    for i in range(0, 48):
        translation_table[i] = '_'
    # From ':' to '@'. See ASCI table for more details.
    for i in range(58, 65):
        translation_table[i] = '_'
    # From symbol '[' to '`'. See ASCI table for more details.
    for i in range(91, 97):
        translation_table[i] = '_'
    # From symbol '{' to [DEL]. See ASCI table for more details.
    for i in range(123, 128):
        translation_table[i] = '_'
    return translation_table

# name = '!@#$%^&*()абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ_АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇГ_0123456789'
# normalize = make_translate_function()
# name = normalize(name)

def make_translate_function():
    translation = make_translate_table()

    def translate(name):
        """Normalize parameter - name"""
        return name.translate(translation)
    return translate

def make_destination(normalize, destination_root: str, name: str) -> str:
    """Create destination path with normalization"""
    sname = os.path.splitext(os.path.basename(name))
    file_name = sname[0]
    ext_name = sname[1]
    if normalize:
        destination_name = normalize(file_name)
    else:
        destination_name = file_name
    destination_name += ext_name
    destination = os.path.join(destination_root, destination_name)
    return destination

def make_copy_file_function(destination_root: str):
    normalize = None
    if not args.use_original_names:
        normalize = make_translate_function()

    def copy_file(name) -> str:
        """Move file to destination directory"""
        if not os.path.exists(name):
            return name
        destination = make_destination(normalize, destination_root, name)
        if args.verbose >= 3:
            print(f"Copy file - {name} to {destination}")
        try:
            shutil.copy2(name, destination)
        except Exception as e:
            print(f"Error: {e}")
        return destination
    return copy_file

def make_move_file_function(destination_root: str):
    normalize = None
    if not args.use_original_names:
        normalize = make_translate_function()

    def move_file(name) -> str:
        """Move file to destination directory"""
        if not os.path.exists(name):
            return name
        destination = make_destination(normalize, destination_root, name)
        if args.verbose >= 3:
            print(f"Move file - {name} to {destination}")
        try:
            shutil.move(name, destination)
        except Exception as e:
            print(f"Error: {e}")
        return destination
    return move_file

def make_unpack_file_function(destination_root: str):
    normalize = None
    if not args.use_original_names:
        normalize = make_translate_function()

    def unpack_file(name) -> str:
        """Unpack archive to destination directory"""
        if not os.path.exists(name):
            return name
        directory_name = os.path.splitext(os.path.basename(name))[0]
        destination = make_destination(
            normalize, destination_root, directory_name)
        if not os.path.exists(destination):
            if args.verbose >= 3:
                print(f"Create directory - {destination}")
            try:
                os.mkdir(destination)
            except Exception as e:
                print(f"Error: {e}")
        try:
            if args.verbose >= 3:
                print(f"Unpack archive - {name} to directory {destination}")
            shutil.unpack_archive(name, destination)
        except shutil.ReadError as e:
            print(f"Error: {e}")
            os.rmdir(destination)
        except Exception as e:
            print(f"Error: {e}")
        return destination
    return unpack_file

def make_delete_file_function(destination_root: str):
    normalize = None
    if not args.use_original_names:
        normalize = make_translate_function()

    def delete_file(name) -> str:
        """Remove archive if it was unpacked successfully"""
        if not os.path.exists(name):
            return name
        directory_name = os.path.splitext(os.path.basename(name))[0]
        destination = make_destination(
            normalize, destination_root, directory_name)
        if os.path.exists(destination):  # Check if archive was unpacked
            if args.verbose >= 3:
                print(f"Remove file - {name}")
            try:
                os.remove(name)
            except Exception as e:
                print(f"Error: {e}")
        return name
    return delete_file


def remove_file(name) -> str:
    """Just remove file"""
    if os.path.exists(name):
        if args.verbose >= 3:
            print(f"Remove file - {name}")
        try:
            os.remove(name)
        except Exception as e:
            print(f"Error: {e}")
    return name

def sort(current_dir: str, dir2ext: dict, ext2dir: dict, result: dict) -> dict:
    dirs = []
    files = []

    # Filling files and subdirectories lists to process
    for f in os.listdir(current_dir):
        pathname = os.path.join(current_dir, f)
        if os.path.isdir(pathname):
            name = os.path.basename(pathname)
            if name in dir2ext:  # Exclude destination directories
                continue
            dirs.append(pathname)
        elif os.path.isfile(pathname):
            files.append(pathname)
        else:  # ignore all other filesystem entities
            pass

    # Process subdirectories
    if dirs:
        for folder in dirs:
            if args.verbose > 0:
                print(f"Processing directory - {folder}")
            result = sort(folder, dir2ext, ext2dir, result)
            if not args.keep_empty_dir and os.path.exists(folder):
                if args.verbose >= 3:
                    print(f"Remove empty directory - {folder}")
                try:
                    os.rmdir(folder)
                except Exception as e:
                    print(f"Error: {e}")

    # Fill result dictionary with files in currrent path
    files_result = {}  # Files to be processed
    for pathname in files:
        name = os.path.basename(pathname)
        if name == 'sorter.py':  # Exclude script
            continue
        ext = os.path.splitext(name)[1].replace('.', '').lower()
        if len(ext2dir) == 1 and '*' in ext2dir:
            target_dir = ext2dir['*']
        elif not ext in ext2dir:  # All unknown extensions put to other
            target_dir = 'other'
        else:
            target_dir = ext2dir[ext]

        if not target_dir in result:
            result[target_dir] = {}
        if not target_dir in files_result:
            files_result[target_dir] = {}

        if not ext in result[target_dir]:
            result[target_dir][ext] = []
        if not ext in files_result[target_dir]:
            files_result[target_dir][ext] = []

        result[target_dir][ext].append(pathname)
        files_result[target_dir][ext].append(pathname)

    # Process files
    for dest, exts in files_result.items():
        for ext, files in exts.items():
            functions = dir2ext[dest]['functions']
            if functions:
                dir_name = os.path.join(target_directory, dest)
                if not os.path.exists(dir_name):
                    if args.verbose >= 2:
                        print(f"Create directory - {dir_name}")
                    os.mkdir(dir_name)
                for function in functions:
                    for name in map(function, files):
                        continue
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Sort files by extension. Can unpack supported archives.")  # ,exit_on_error=False
    parser.add_argument(
        "directories",
        help="Directories list to process, if not specified used current directory",
        action="store",
        nargs='*'
    )  # , type=pathlib.Path)
    parser.add_argument(
        "-k", "--keep-empty-dir",
        help="Don't remove empty directories",
        action="store_true",
        required=False
    )
    parser.add_argument(
        "-u", "--use-original-names",
        help="Don't normalize file and directory(for unpacking archives) names",
        action="store_true",
        default=False,
        required=False
    )
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="count", default=0, required=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--settings",
        help="Specify path to settings(JSON) file",
        metavar="settings.json",
        default="settings.json",
        required=False
    )
    group.add_argument(
        "-d", "--destination",
        help="Destination directory",
        metavar="destination",
        action="store",
        default="",
        required=False
    )
    parser.add_argument(
        "-e", "--extensions",
        help="File's extensions",
        metavar="extensions",
        action="store",
        default="*",
        required=False,
        nargs='*'
    )
    parser.add_argument(
        "-f", "--functions",
        help="Function's list(order sensitive)",
        metavar="functions",
        action="store",
        default="move",
        required=False,
        nargs='*'
    )

    args = parser.parse_args()

    if not len(args.directories):
        # If no directories specified, use current
        path = os.path.split(sys.argv[0])
        args.directories.append(path[0])

    dir2ext = {}
    if args.destination:  # and args.extensions and args.functions:
        dir2ext[args.destination] = {}
        dir2ext[args.destination]['extensions'] = args.extensions
        dir2ext[args.destination]['functions'] = args.functions
    elif os.path.exists(args.settings):
        # Load settings from file
        with open(args.settings, 'r') as settings:
            dir2ext = json.load(settings)
    else:
        # Default settings
        # Supported functions:
        #   copy, move, remove, unpack, delete(used for removing archives)
        #   order sensitive
        dir2ext = {
            'archives'  :   {
                'extensions'    :   ['zip', 'tar', 'tgz', 'gz', '7zip', '7z', 'iso', 'rar'],
                'functions'     :   ['unpack', 'move']
            },

            'video'     :   {
                'extensions'    :   ['avi', 'mp4', 'mov', 'mkv'],
                'functions'     :   ['move']
            },
            'audio'     :   {
                'extensions'    :   ['wav', 'mp3', 'ogg', 'amr'],
                'functions'     :   ['move']
            },
            'documents' :   {
                'extensions'    :   ['doc', 'docx', 'txt', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx', 'rtf', 'xml', 'ini'],
                'functions'     :   ['move']
            },
            'images'    :   {
                'extensions'    :   ['jpeg', 'png', 'jpg', 'svg'],
                'functions'     :   ['move']
            },
            'software'  :   {
                'extensions'    :   ['exe', 'msi', 'bat', 'dll'],
                'functions'     :   ['move']
            },
            'other'     :   {
                'extensions'    :   [],
                'functions'     :   ['move']
            }
        }

    # Generate mapping - extension to directory,
    # used to resolve desctination directory by file extension
    ext2dir = {}
    for folder, extensions in dir2ext.items():
        for ext in extensions['extensions']:
            ext2dir[ext] = folder

    # Replace function name with real functions
    for target_directory in args.directories:
        if os.path.exists(args.settings):
            _dir2ext = deepcopy(dir2ext)
            for folder, extensions in _dir2ext.items():
                # Fill dir2ext.extensions['functions']
                if 'functions' in extensions and extensions['functions']:
                    if isinstance(extensions['functions'], str):
                        function = extensions['functions']
                        extensions['functions'] = []
                        extensions['functions'].append(function)
                    functions = []
                    for function in extensions['functions']:
                        if function:
                            function = function.lower()
                            function_name = (
                                'make_' + function + '_file_function')
                            if function_name in globals():
                                functions.append(globals()[function_name](
                                    os.path.join(target_directory, folder)))
                            function_name = (function + '_file')
                            if function_name in globals():
                                functions.append(globals()[function_name])
                    extensions['functions'] = functions

            result = {}
            result = sort(target_directory, _dir2ext, ext2dir, result)
            if args.verbose >= 4:
                print(f"Processed dictionary: {result}")
        else:
            print(f"Error: directory {target_directory} does not exist")
