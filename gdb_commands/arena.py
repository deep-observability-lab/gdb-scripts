import gdb
from global_state import state_manager
from pretty_print import PrettyPrinter

class Arena(gdb.Command):

    def __init__(self):
        super(Arena, self).__init__("arena", gdb.COMMAND_USER)

    def get_arena_info(self, arena):
        start_address = int(arena.address)
        arena_size = int(arena['system_mem'])
        end_address = start_address + arena_size
        return start_address, end_address

    def invoke(self, arg, from_tty):
        # Clear the previous list of arenas
        state_manager.arenas = []

        # Fetch the main_arena
        main_arena = gdb.parse_and_eval('main_arena')
        current_arena = main_arena
        next_arena_address = 0

        # Print header for Arena Information
        PrettyPrinter.print_line('=' * 70)
        PrettyPrinter.print_centered("Arena Information", width=70)
        PrettyPrinter.print_line('=' * 70)

        # Traverse through the arenas
        index = 0
        while True:
            start_address, end_address = self.get_arena_info(current_arena)

            # Store the start address in state_manager
            state_manager.arenas.append(f"0x{start_address:x}")

            # Pretty print the arena information
            label = f"Arena {index} at 0x{start_address:x}"
            PrettyPrinter.print_row(
                label, f"Start = 0x{start_address:x}, End = 0x{end_address:x}", width=70)

            # Move to the next arena
            next_arena_address = current_arena['next']
            if next_arena_address == main_arena.address:
                break
            current_arena = next_arena_address.dereference()
            index += 1

        # Print footer for Arena Information
        PrettyPrinter.print_line('=' * 70)


# Register the command with GDB
Arena()
