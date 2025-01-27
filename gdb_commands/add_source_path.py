import os
import gdb


class AddChildDirectories(gdb.Command):
    """
    A GDB command to add all child directories inside a given parent directory to GDB's source path.

    Usage:
        add_child_dirs <parent_path>
    Example:
        (gdb) add_child_dirs /home/victim/src
    """

    def __init__(self):
        super(
            AddChildDirectories,
            self).__init__(
            "add_child_dirs",
            gdb.COMMAND_SUPPORT)

    def invoke(self, argument, from_tty):
        # Get the parent path from the command arguments
        parent_path = argument.strip()
        if not parent_path:
            print(
                "Error: Please provide the parent path. Usage: add_child_dirs <parent_path>")
            return

        if not os.path.exists(parent_path):
            print(f"Error: The path '{parent_path}' does not exist.")
            return

        if not os.path.isdir(parent_path):
            print(f"Error: The path '{parent_path}' is not a directory.")
            return

        unique_paths = set()  # Use a set to store unique paths

        # Collect all unique child directories
        for root, dirs, _ in os.walk(parent_path):
            for directory in dirs:
                child_path = os.path.join(root, directory)
                unique_paths.add(child_path)

        # Loop over unique paths and execute GDB commands
        for child_path in sorted(unique_paths):  # Sorted for consistency
            try:
                gdb.execute(f"dir {child_path}")
            except gdb.error as e:
                print(f"Error executing GDB command for {child_path}: {e}")
