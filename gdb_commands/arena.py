import gdb
from global_state import state_manager
from pretty_print import PrettyPrinter


class Arena(gdb.Command):

    def __init__(self):
        super(Arena, self).__init__("arena", gdb.COMMAND_USER)

    def get_arena_info(self, arena):
        """Extract the start and end address of the arena."""
        try:
            start_address = int(arena.address)
            arena_size = int(arena['system_mem'])
            end_address = start_address + arena_size
            max_system_mem = int(arena['max_system_mem'])
            top_chunk = arena['top']
            return start_address, end_address, arena_size, max_system_mem, top_chunk
        except (gdb.MemoryError, gdb.error) as e:
            PrettyPrinter.print_error("Error accessing arena: {}".format(e))
            return None

    def invoke(self, arg, from_tty):
        """GDB command to display information about the arenas."""
        state_manager.arenas = []

        try:
            main_arena = gdb.parse_and_eval('main_arena')
        except gdb.error as e:
            PrettyPrinter.print_error(
                "Error accessing main_arena: {}".format(e))
            return

        current_arena = main_arena
        table_width = 120

        PrettyPrinter.print_header("Arena Information", width=table_width)

        index = 0
        max_iterations = 100  # Safeguard against infinite loops

        while index < max_iterations:
            arena_info = self.get_arena_info(current_arena)
            if arena_info is None:
                break

            start_address, end_address, arena_size, max_system_mem, top_chunk = arena_info

            state_manager.arenas.append("0x{:x}".format(start_address))

            label = "Arena {} at 0x{:x}".format(index, start_address)
            data = "Start = 0x{:x}, End = 0x{:x}, Size = {}".format(
                start_address, end_address, arena_size)
            PrettyPrinter.print_row(label, data, width=table_width)

            next_arena_address = current_arena['next']
            if next_arena_address == main_arena.address:
                break
            current_arena = next_arena_address.dereference()
            index += 1

        if index >= max_iterations:
            PrettyPrinter.print_error(
                "Potential infinite loop detected in arena traversal.")

        PrettyPrinter.print_footer(width=table_width)
