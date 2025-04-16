import gdb
import os
import re
from gdb_commands.pretty_print import PrettyPrinter
from gdb_commands.global_state import state_manager


class Process(gdb.Command):
    def __init__(self):
        super(Process, self).__init__("process", gdb.COMMAND_USER)

    def count_mmaped_blks(self):
        """Count the number of mmaped blocks and their total size using mallinfo()."""
        try:
            if not state_manager.is_process:
                PrettyPrinter.print_error("Not supported in coredump debugging")
                return None, None
            try:
                # Explicitly cast mallinfo call to its return type
                gdb.execute('set $mi = (struct mallinfo) mallinfo()', to_string=True)
                mmap_info = gdb.parse_and_eval('$mi')
                num_regions = int(mmap_info['hblks'])
                total_size = int(mmap_info['hblkhd'])
                return num_regions, total_size
            except gdb.error as e:
                PrettyPrinter.print_error(f"mallinfo() not accessible: {e}\n mmap_info are not accessable.")
                return 0, 0            

        except Exception as e:
            PrettyPrinter.print_error(f"Unexpected error fetching mmap information: {e}")
            return 0, 0


    def get_absolute_executable_path(self, pid):
        """Get the absolute path of the executable for the given process ID."""
        gdb_output = gdb.execute("info proc exe", to_string=True)
        match = re.search(r"exe = '(.+)'", gdb_output)

        if match:
            exe_path = match.group(1)
            return exe_path
        else:
            PrettyPrinter.print_error("can not get the executable path.")

        # if "process executable is" in absolute_path :
        #     return absolute_path
        # else :
        #     return "<unknown>"

    def invoke(self, arg, from_tty):
        """GDB command to display process information."""
        try:
            # Fetch process information
            inferior = gdb.selected_inferior()
            pid = inferior.pid
            if pid == 0:
                print("No process is currently being debugged.")
                return

            thread_num = len(inferior.threads())
            binary_path = self.get_absolute_executable_path(pid)

            # Fetch mmap info
            num_regions, total_size = self.count_mmaped_blks()

            # Define table width for pretty printing
            table_width = 70

            header_color = PrettyPrinter.HEADER_COLOR
            label_color = PrettyPrinter.LABEL_COLOR
            reset_color = PrettyPrinter.RESET_COLOR

            # Pretty print the output with colors
            PrettyPrinter.print_header(
                "{}Process Information{}".format(
                    header_color, reset_color), width=table_width)
            PrettyPrinter.print_row(
                "{}Running File:{}".format(
                    label_color,
                    reset_color),
                binary_path,
                width=table_width)
            PrettyPrinter.print_row(
                "{}Process ID:{}".format(
                    label_color,
                    reset_color),
                str(pid),
                width=table_width)
            PrettyPrinter.print_row(
                "{}Number of Threads:{}".format(
                    label_color,
                    reset_color),
                str(thread_num),
                width=table_width)
            PrettyPrinter.print_row(
                "{}Number of mmapped regions:{}".format(
                    label_color,
                    reset_color),
                str(num_regions),
                width=table_width)
            PrettyPrinter.print_row("{}Space in mmapped regions (bytes):{}".format(
                label_color, reset_color), str(total_size), width=table_width)
            PrettyPrinter.print_footer(width=table_width)

        except gdb.error as e:
            print("Error in process command: {}".format(e))

