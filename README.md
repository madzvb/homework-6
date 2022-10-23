# homework-6
usage: sorter.py [-h] [-k] [-u] [-o] [-v] [-s settings.json | -d destination]
                 [-e [extensions ...]] [-f [functions ...]]
                 [directories ...]

Sort files by extension. Can unpack supported archives. Cautions: All files
with same name will be overwrited by default!

positional arguments:
  directories           Directories list to process, if not specified used
                        current directory.

options:
  -h, --help            show this help message and exit
  -k, --keep-empty-dir  Don't remove empty directories.
  -u, --use-original-names
                        Don't normalize file and directory(for unpacking
                        archives) names.
  -o, --overwrite       Overwrite existing files and directories.
  -v, --verbose         increase output verbosity.
  -s settings.json, --settings settings.json
                        Specify path to settings(JSON) file
  -d destination, --destination destination
                        Destination directory
  -e [extensions ...], --extensions [extensions ...]
                        File's extensions
  -f [functions ...], --functions [functions ...]
                        Function's list(order sensitive)
