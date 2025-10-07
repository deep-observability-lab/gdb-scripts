import gdb
from gdb_commands.global_state import state_manager
import re
from gdb_commands.pretty_print import PrettyPrinter
import traceback

label_color = PrettyPrinter.LABEL_COLOR
reset_color = PrettyPrinter.RESET_COLOR

class MemRegion():
    def __init__(self):
        self.start = ''
        self.end = ''
        self.size = 0
        self.offset = 0x00
        self.is_main = False
        self.ar_add = ''
        self.is_first = False

    def __str__(self) -> str:
        strr = "starts at: {} , ends at: {} with arena: {} and size {}".format(
            self.start, self.end, self.ar_add, self.size)

        if self.is_main:
            return "Main heap:\t" + strr
        return strr


class Heap(gdb.Command):

    def __init__(self):
        super(Heap, self).__init__("heap", gdb.COMMAND_USER)
        self.mmap = None
        self.total = None
        self.free = None
        self.used = None

    def read_memory(self, start_address, size):
        try:
            inferior = gdb.selected_inferior()
            memory = inferior.read_memory(start_address, size)
            value_as_int = int.from_bytes(
                memory, byteorder=state_manager.byteorder)
            return value_as_int
        except gdb.error:
            print(
                "Error: Cannot read memory at address {}. ".format(hex(start_address)))
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def count_memory_usage(self, heap_start, heap_end):
        allocated = 0
        total = heap_end - heap_start
        alignment = 0x0
        arch = 64
        try:
            word_size = gdb.parse_and_eval("sizeof(void*)")
            if word_size == 4:
                arch = 32
            if arch == 64:
                alignment = 0x10  # 16-byte alignment for 64-bit systems
            else:
                alignment = 0x8

            cur = (heap_start + alignment - 1) & ~(alignment - 1)
            if cur < heap_start:
                cur += alignment

            nxhdr = 0
            size_t = gdb.lookup_type('size_t').pointer().sizeof
            while (cur != heap_end):
                num_words = 4
                value = self.read_memory(cur + size_t, num_words)
                sz = value & ~0x7
                nxhdr = cur + sz
                if nxhdr == heap_end:
                    break
                if sz == 0:
                    break
                value = self.read_memory(nxhdr + size_t, num_words)
                pbit = (value & 0x1)

                cur = nxhdr

                if pbit == 1:
                    allocated += sz

            PrettyPrinter.print_row(
                "{}allocated size : {}".format(
                    label_color,
                    reset_color),
                allocated,
                width=100)
            state_manager.used_mem += allocated
            state_manager.total_heap += total
        except gdb.error as e:
            PrettyPrinter.print_error(f"GDB Command Error: {e}")
            return 0
        except Exception as e:
            PrettyPrinter.print_error(f"Unexpected Error: {e}")
            return 0
        
    def extract_heap_info(self):
        heap_sections = []
        gdb_command = "info proc mappings"
        regex = r'^\s*([0-9a-fx]+)\s+([0-9a-fx]+)\s+([0-9a-fx]+)\s+[0-9a-fx]+\s*$'
        
        try:    
            if not state_manager.is_process:
                gdb_command = "maintenance info sections"
                regex = r'^\s*\[\d+\]\s+([0-9a-fA-Fx]+)->([0-9a-fA-Fx]+).*?:.*?ALLOC\s+LOAD\s+HAS_CONTENTS$'
            
            mappings_output = gdb.execute(gdb_command, to_string=True)
            lines = mappings_output.splitlines()

            for line in lines:
                match = re.match(regex, line)
                if match:
                    heap = MemRegion()
                    heap.start = str(match.group(1)).strip()
                    heap.end = str(match.group(2)).strip()
                    heap_sections.append(heap)
            
            return heap_sections

        except gdb.error as e:
            PrettyPrinter.print_error(f"GDB Command Error: {e}")
            return []
        except Exception as e:
            PrettyPrinter.print_error(f"Unexpected Error: {e}")
            return []

    def extract_heaps(self):
        self.extract_main_heap()
        regions = self.extract_heap_info()
        try:
            if len(regions) != 0:
                for r in regions:
                    memory = gdb.parse_and_eval(
                        "*(struct _heap_info*) {}".format(r.start))
                    ss = str(memory['ar_ptr']).strip()
                    
                    if ss in state_manager.arenas:
                        r.ar_add = str(memory['ar_ptr'])

                        if r.ar_add != str(
                                hex((int(r.start, 16) + state_manager.HEAPINFO_SIZE))):
                            r.offset = str(
                                hex((int(r.start, 16) + state_manager.HEAPINFO_SIZE)))
                        else:
                            r.offset = str(
                                hex(int(r.start, 16) + state_manager.ARENA_SIZE + state_manager.HEAPINFO_SIZE))

                        r.size = int(str(memory['size']))
                        if str(memory['prev']) == '0x0':
                            r.is_first = True
                        if r.ar_add not in state_manager.arena2heaps:
                            state_manager.arena2heaps[r.ar_add] = []
                        state_manager.arena2heaps[r.ar_add].append(
                            len(state_manager.heaps))
                        
                        state_manager.heaps.append(r)
                for ar in state_manager.arenas:
                    if ar not in state_manager.arena2heaps:
                        state_manager.arena2heaps[ar] = []
        except gdb.error as e:
            PrettyPrinter.print_error(f"GDB Command Error: {e}")
            return
        except Exception as e:
            PrettyPrinter.print_error(f"Unexpected Error: {e}")
            return

    def test_offset_for_main_heap(self, heap_start):
        num_words = 4
        shift = 4
        align = 16
        word_size = gdb.parse_and_eval("sizeof(void*)")
        if word_size == 4:
            align = 8

        size_t = gdb.lookup_type('size_t').pointer().sizeof

        for i in range(9):
            value = self.read_memory(
                heap_start + size_t + shift * i, num_words)
            sz = value & ~0x7
            if sz != 0 and ((sz % align) == 0):
                return shift * i
        return 0


    def extract_main_heap(self):
    # Initialize the main heap region object
        main_heap = MemRegion()
        
        try:
            # Extract the base address of the heap (sbrk_base)
            main_heap.start = gdb.execute(
                'p mp_.sbrk_base',
                to_string=True).strip().split(' = ')[1].strip('"')

            # Check if sbrk_base is zero (corruption or missing initialization)
            if main_heap.start == '0x0':
                PrettyPrinter.print_warning("Warning: sbrk_base is 0. Heap might not be initialized or the process is using mmap.")
                return

            # Extract the top chunk address from main_arena
            top_chunk = gdb.execute(
                'p main_arena.top',
                to_string=True)

            # Check if main_arena.top could not be retrieved
            if "mchunkptr" not in top_chunk:
                PrettyPrinter.print_warning("Warning: Unable to retrieve main_arena.top. This could indicate heap corruption.")
                return

            # Extract the hex address of the top chunk
            pattern = r"0x[0-9a-fA-F]+"
            match = re.search(pattern, top_chunk)

            if not match:
                PrettyPrinter.print_warning("Warning: Unable to find valid address for top chunk. Potential memory corruption.")
                return

            hex_address = match.group()
            num_words = 1

            # Read memory at the top chunk address
            value = self.read_memory(int(hex_address, 16), num_words)
            # Calculate the size of the top chunk
            sz = value & ~0x7
            main_heap.end = str(hex(int(hex_address, 16) + sz))

            # Calculate the total size of the heap region
            total = int(main_heap.end, 16) - int(main_heap.start, 16)

            if total <= 0:
                PrettyPrinter.print_warning("Warning: Invalid heap size (total <= 0). This could indicate heap corruption.")
                return

            # Set heap size and arena address
            main_heap.size = total
            main_heap.ar_add = state_manager.arenas[0]
            main_heap.is_main = True

            # Check for heap offset (potential issue with invalid memory address)
            shift = self.test_offset_for_main_heap(int(main_heap.start, 16))
            if shift < 0:
                PrettyPrinter.print_warning("Warning: Invalid offset calculated for main heap. Potential corruption detected.")
                return

            main_heap.offset = str(hex(int(main_heap.start, 16) + shift))

            # Store the main heap region
            state_manager.arena2heaps[main_heap.ar_add] = [0]
            state_manager.heaps.append(main_heap)

        except gdb.error as e:
            PrettyPrinter.print_error(f"GDB Command Error: {e}")
            return
        except Exception as e:
            PrettyPrinter.print_error(f"Unexpected Error: {e}")
            return

    def invoke(self, arg, from_tty):
        table_width = 100
        
        state_manager.heaps = []
        state_manager.arena2heaps = {}
        self.extract_heaps()
        cnt = 0
        PrettyPrinter.print_header(
            "analysis thread's heaps", width=table_width)
        for ar in state_manager.arenas:
            if ar in state_manager.arena2heaps.keys():
                if len(state_manager.arena2heaps[ar]) > 0:
                    for heap_indx in state_manager.arena2heaps[ar]:
                        tmp_heap = state_manager.heaps[heap_indx]
                        end = int(tmp_heap.end, 16)
                        start = int(tmp_heap.offset, 16)
                        if (int(tmp_heap.ar_add, 16) == int(tmp_heap.offset, 16)):
                            start += state_manager.ARENA_SIZE
                        PrettyPrinter.print_devider(100)
                        PrettyPrinter.print_half_header("heap #{}:".format(cnt))
                        PrettyPrinter.print_row(
                            "{}starts at : {}".format(
                                label_color,
                                reset_color),
                            tmp_heap.start,
                            width=table_width)
                        PrettyPrinter.print_row(
                            "{}ends at : {}".format(
                                label_color,
                                reset_color),
                            tmp_heap.end,
                            width=table_width)
                        PrettyPrinter.print_row(
                            "{}with arena : {}".format(
                                label_color,
                                reset_color),
                            tmp_heap.ar_add,
                            width=table_width)
                        PrettyPrinter.print_row(
                            "{}with size : {}".format(
                                label_color,
                                reset_color),
                            tmp_heap.size,
                            width=table_width)
                        cnt += 1
                        self.count_memory_usage(start, end)

        PrettyPrinter.print_footer(100)
