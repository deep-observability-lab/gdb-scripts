import gdb
import sys


class GlobalState:
    def __init__(self):
        self.bins = []
        self.arenas = []
        self.heaps = []
        self.arena2heaps = {}
        heap_info_type = gdb.lookup_type('heap_info')
        self.HEAPINFO_SIZE = heap_info_type.sizeof
        malloc_state_type = gdb.lookup_type('struct malloc_state')
        self.ARENA_SIZE = malloc_state_type.sizeof
        self.byteorder = sys.byteorder
        self.word_size = gdb.lookup_type('void').pointer().sizeof


state_manager = GlobalState()
