import gdb
import os
from pretty_print import PrettyPrinter

class Process(gdb.Command):

    def __init__(self):
        super(Process, self).__init__("process", gdb.COMMAND_USER)
        print("Process command initialized.")

    def count_mmaped_blks(self):
        mmap = gdb.parse_and_eval('mallinfo()')
        num_regions = mmap['hblks']
        total_size = mmap['hblkhd']
        return num_regions, total_size

    def get_absolute_executable_path(self, pid):
        # Read the /proc/[pid]/cmdline file
        cmdline_path = f"/proc/{pid}/cmdline"
        try:
            with open(cmdline_path, "r") as f:
                cmdline = f.read().split('\0')

            # Get the first element, which is the executable path
            executable_path = cmdline[0]

            # Convert to an absolute path and resolve symbolic links
            absolute_path = os.path.realpath(os.path.abspath(executable_path))
            return absolute_path
        except Exception as e:
            print(f"Error reading executable path: {e}")
            return "<unknown>"

    def invoke(self, arg, from_tty):
        # Fetch process information
        inferior = gdb.selected_inferior()
        pid = inferior.pid
        thread_num = len(inferior.threads())
        binary_path = self.get_absolute_executable_path(pid)

        # Fetch mmap info
        num_regions, total_size = self.count_mmaped_blks()

        # Define table width for pretty printing
        table_width = 70

        # Pretty print the output
        PrettyPrinter.print_header("Process Information", width=table_width)
        PrettyPrinter.print_row("Running File:", binary_path, width=table_width)
        PrettyPrinter.print_row("Process ID:", pid, width=table_width)
        PrettyPrinter.print_row("Number of Threads:", thread_num, width=table_width)
        PrettyPrinter.print_row("Number of mmapped regions:", num_regions, width=table_width)
        PrettyPrinter.print_row("Space in mmapped regions (bytes):", total_size, width=table_width)
        PrettyPrinter.print_footer(width=table_width)

# Register the command with GDB
Process()
