from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import sys


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


if __name__ == '__main__':

    file_path = sys.argv[1]
    pattern = sys.argv[2]
    subst = sys.argv[3]
    print(file_path)
    print(pattern)
    print(subst)
    replace(file_path, pattern, subst)
