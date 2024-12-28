import gdb
import os
import re 

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
    sources_output = get_info_sources()
  
    # Split the output into lines and extract directories
    source_dirs = set()
    for line in sources_output.splitlines():
        # Extract the directory from the line
        line = line.strip()
        # if line and os.path.isdir(line):
        source_dirs.add(os.path.abspath(line))

    # Get the absolute path of the target directory
    target_path_abs = os.path.abspath(target_path)
    # Find matching directories
    print("target : " , target_path_abs )
    matching_dirs = []
    dirs = get_directory_names(target_path_abs )
    for source_dir in dirs :
        print( source_dir)
        if target_path_abs in source_dir:
            matching_dirs.append(source_dir)

    return matching_dirs

# Example usage
if __name__ == "__main__":
    target_directory = "../workspace/"  # Replace with your target directory
    matching_directories = find_matching_directories(target_directory)
    
    print("Matching directories:")
    for directory in matching_directories:
        print(directory)

# https://gist.github.com/ricksladkey/bdcd761a5b06e3d670728d8cc96458ba