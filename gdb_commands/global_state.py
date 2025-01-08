import gdb
import sys


class GlobalState:
    def __init__(self):
        self.bins = []
        self.arenas = []
        self.heaps = []
        self.arena2heaps = {}

        # Initialize word size
        try:
            self.word_size = gdb.lookup_type('void').pointer().sizeof
        except gdb.error as e:
            print(f"Error initializing word_size: {e}")
            self.word_size = None  # Set a default value or handle as needed

        # Check and print the endianness
        try:
            byte_order = gdb.execute("show endian", to_string=True)
            if "little" in byte_order:
                self.byteorder = 'little'
            elif "big" in byte_order:
                self.byteorder = 'big'
            else:
                print("Could not determine endianness.")
                self.byteorder = None  # Set a default value or handle as needed
        except gdb.error as e:
            print(f"Error determining endianness: {e}")
            self.byteorder = None  # Set a default value or handle as needed

        # Initialize HEAPINFO_SIZE
        try:
            heap_info_type = gdb.lookup_type('heap_info')
            self.HEAPINFO_SIZE = heap_info_type.sizeof
        except gdb.error as e:
            print(f"Error initializing HEAPINFO_SIZE: {e}")
            self.HEAPINFO_SIZE = None  # Set a default value or handle as needed

        # Initialize ARENA_SIZE
        try:
            malloc_state_type = gdb.lookup_type('struct malloc_state')
            self.ARENA_SIZE = malloc_state_type.sizeof
        except gdb.error as e:
            print(f"Error initializing ARENA_SIZE: {e}")
            self.ARENA_SIZE = None  # Set a default value or handle as needed

        # Check if attached to a process
        self.is_process = self.is_attached_process()

    def is_attached_process(self):
        try:
            result = gdb.execute("p getpid()", to_string=True)
            return True
        except gdb.error as e:
            return False


# Create an instance of GlobalState
state_manager = GlobalState()
