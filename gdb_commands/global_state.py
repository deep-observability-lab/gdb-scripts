import gdb
#set default valuees for size of structs 
ARENA_SIZE = 0x450
HEAPINFO_SIZE = 0x10
SYSTEM = 4 

class GlobalState:
    def __init__(self ) : 
        self.bins = []
        self.arenas = []
        self.heaps = []
        self.arena2heaps = {}
        heap_info_type = gdb.lookup_type('heap_info')
        HEAPINFO_SIZE = heap_info_type.sizeof
        malloc_state_type = gdb.lookup_type('struct malloc_state')
        ARENA_SIZE = malloc_state_type.sizeof
        
state_manager = GlobalState()
