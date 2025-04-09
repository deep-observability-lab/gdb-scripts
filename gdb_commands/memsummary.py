import gdb
from gdb_commands.global_state import state_manager
from gdb_commands.pretty_print import PrettyPrinter


class MemSummary(gdb.Command):
    def __init__(self):
        super(MemSummary, self).__init__("memsummary", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        """GDB command to display memory usage information for a glibc application."""
        # Retrieve memory stats from the state manager
        used_mem = state_manager.used_mem
        freed_mem = state_manager.freed_mem
        total_heap = state_manager.total_heap
        leak_mem = used_mem - freed_mem  # Calculate memory leak

        # Prevent division by zero
        def percentage(part, whole):
            return (part / whole * 100) if whole else 0

        used_percent = percentage(used_mem, total_heap)
        freed_percent = percentage(freed_mem, total_heap)
        leak_percent = percentage(leak_mem, total_heap)

        # Print the formatted memory summary
        width = 60
        PrettyPrinter.print_header("Memory Summary", width)
        PrettyPrinter.print_row("Total Heap", f"{total_heap} bytes", width)
        PrettyPrinter.print_row("Used Memory", f"{used_mem} bytes ({used_percent:.2f}%)", width)
        PrettyPrinter.print_row("Freed Memory", f"{freed_mem} bytes ({freed_percent:.2f}%)", width)

        # Use red for memory leaks if any
        if leak_mem > 0:
            PrettyPrinter.print_row("Memory Leak", PrettyPrinter.RED_COLOR + f"{leak_mem} bytes ({leak_percent:.2f}%)" + PrettyPrinter.RESET_COLOR, width)
        else:
            PrettyPrinter.print_row("Memory Leak", f"{leak_mem} bytes ({leak_percent:.2f}%)", width)

        PrettyPrinter.print_footer(width)

