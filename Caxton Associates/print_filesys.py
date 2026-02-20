import os
from os.path import join, isdir, isfile

def print_filesys(root_dir):
    """
    Traverses a directory structure and prints contents starting from the deepest level first.
    Prints both the folder/file name and the object type (file or folder).
    
    Args:
        root_dir: The root directory path to traverse
    """
    # Use topdown=False to traverse from deepest level first
    # This visits subdirectories before their parent directories
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Print files in the current directory first (they are at the deepest level)
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # Explicitly check and print the object type
            if os.path.isfile(file_path):
                object_type = "file"
            elif os.path.isdir(file_path):
                object_type = "folder"
            else:
                object_type = "unknown"
            print(f"{file_path} - {object_type}")
        
        # Then print the current directory itself
        # Explicitly check and print the object type
        if os.path.isdir(dirpath):
            object_type = "folder"
        else:
            object_type = "unknown"
        print(f"{dirpath} - {object_type}")

def print_filesys_recursive(path):
    if isfile(path):
        print(f'{path} - file')
        return

    files = []
    for content in os.listdir(path):
        full_path = join(path, content)
        if isdir(full_path):
            print_filesys_recursive(full_path)
        elif isfile(full_path):
            files.append(full_path)
        else:
            print(f'{full_path} - unknown')
        
    for file in files:
        print(f'{file} - file')

    print(f'{path} - folder')


def print_filesys_memo(root: str):
    if isfile(root):
        print(f'{root} - file')
        return

    stack = [root]
    has_seen = set()
    while stack:
        path = stack.pop()
        if isfile(path):
            print(f'{path} - file')
        elif path not in has_seen:
            stack.append(path)
            has_seen.add(path)
            sub_folders = []
            for content in os.listdir(path):
                full_path = join(path, content)
                if isfile(full_path):
                    stack.append(full_path)
                else:
                    sub_folders.append(full_path)
            stack.extend(sub_folders)
        else:
            print(f'{path} - folder')


    
if __name__ == '__main__':
    # print_filesys('/Users/sheryllan/Interviews/Java')
    print_filesys_memo('/Users/sheryllan/Interviews/Java')
    # print_filesys_recursive('/Users/sheryllan/Interviews/Java')