# homework-6
usage: sorter.py [-h] [-k] [-u] [-o] [-v] [-s settings.json | -d destination]
                 [-e [extensions ...]] [-f [functions ...]]
                 [directories ...]

Sort files by extension. Can unpack supported archives.

positional arguments:
  directories           Directories list to process, if not specified used current directory.

options:
  -h, --help            show this help message and exit
  -k, --keep-empty-dir  Don't remove empty directories.
  -u, --use-original-names
                        Don't normalize file and directory(for unpacking archives) names.
  -o, --overwrite       Overwrite existing files and directories.
  -v, --verbose         increase output verbosity.
                            0 - Only errors printout
                            1 - Add warnings
                            2 - Add destination directory creation
                            3 - Add all filesystem modification
                            4 - Add internal script structures
  -s settings.json, --settings settings.json
                        Specify path to settings(JSON) file. Ex: settings.json
  -d destination, --destination destination
                        Destination directory.
  -e [extensions ...], --extensions [extensions ...]
                        File's extensions. Ex: 'jpg jpeg png bmp'
  -f [functions ...], --functions [functions ...]
                        Functions' list(order sensitive).
                            A list of next functions:
                            copy, move, unpack, delete(check if archive already unpacked), remove.
                            Ex: 'unpack move' - will unpack archive file to destination directory
                            and move it to same path.

Usage examples:
            sorter.py -v -o /usr/home/root/downloads /usr/home/root/must_be_sorted -s settings.json
        or  sorter.py -v -o /usr/home/root/downloads /usr/home/root/must_be_sorted -d images -e jpg bmp jpeg -f move
