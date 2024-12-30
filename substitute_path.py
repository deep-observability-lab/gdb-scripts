import gdb
import os
import re 
from pathlib import Path


def get_info_sources():
    """Get the output of the 'info sources' command in GDB."""
    try:
        result = gdb.execute("info sources" , to_string=True)
        return result
    except gdb.error as e:
        print(f"Error executing GDB command: {e}")
        return ""

def get_directory_names(target_path_abs):
    # Create a Path object
    path = Path(target_path_abs)
    # Get all directories in the given path
    try:
        directories = [entry.name for entry in path.iterdir() if entry.is_dir()]
        return directories
    except Exception as e:
        print(f"Error accessing the directory: {e}")
        return []


def find_matching_directories(target_path):
    """Find directories in the output of 'info sources' that match the target path."""
    # Get the output of 'info sources'
    sources_output = get_info_sources().split(',')
    
    # Split the output into lines and extract directories
    source_dirs = set()
    for line in sources_output:
        # Extract the directory from the line
        line = line.strip()
       
        source_dirs.add(line)
    
    # Get the absolute path of the target directory
    target_path_abs = os.path.abspath(target_path)
    # Find matching directories
    
    matching_dirs = set()
    dirs = get_directory_names(target_path_abs )
    for source_dir in dirs :
     
        for p in source_dirs: 
            if source_dir in p:
                p_path = p.split( source_dir)[0]
               
                matching_dirs.add(p_path)
    print(matching_dirs )
    return matching_dirs

def substitute_path(paths, target_path):
    for path in paths:
        try:
            # Construct and execute the GDB command within the GDB environment
            gdb.execute(f"set substitute-path {path} {target_path}")
            # result += f"set substitute-path {path} {target_path}\n"
            print(f"Substitute path command executed for: {path}")
        except gdb.error as e:
            print(f"Error executing substitute-path for {path}: {e}")


def substitution(target_directory ):
    matching_directories = find_matching_directories(target_directory)
    substitute_path(matching_directories , target_directory )

