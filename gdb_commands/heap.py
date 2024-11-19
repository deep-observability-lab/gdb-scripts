import gdb
from global_state import state_manager
import re
import struct
from pretty_print import PrettyPrinter

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

    def count_memory_usage(self, inferior, heap_start, heap_end):
        allocated = 0
        total = heap_end - heap_start

        alignment = 0x0
        arch = 64
        word_size = gdb.parse_and_eval("sizeof(void*)")
        if word_size == 4 : 
            arch = 32

        if arch == 64:
            alignment = 0x10  # 16-byte alignment for 64-bit systems
        else:
            alignment = 0x8

        cur = heap_start & ~(alignment - 1)
        if cur < heap_start:
            cur += alignment

        nxhdr = 0
        
        while (cur != heap_end):
            num_words = 1
            memory = inferior.read_memory(
                cur + state_manager.word_size, num_words * 4)

            word = memory[0:4]
            value = int.from_bytes(word, byteorder=state_manager.byteorder)
            sz = value & ~0x7

            nxhdr = cur + sz
            if nxhdr == heap_end:
                break
            memory = inferior.read_memory(
                nxhdr + state_manager.word_size, num_words * 4)
            word = memory[0:4]
            value = int.from_bytes(word, byteorder=state_manager.byteorder)

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
       

    def extract_heap_info(self):
        mappings_output = gdb.execute("info proc mappings", to_string=True)
        heap_sections = []
        lines = mappings_output.splitlines()
        regex = r'^\s*([0-9a-fx]+)\s+([0-9a-fx]+)\s+([0-9a-fx]+)\s+[0-9a-fx]+\s*$'

        for line in lines:
            match = re.match(regex, line)
            if match:
                heap = MemRegion()
                heap.start = str(match.group(1)).strip()
                heap.end = str(match.group(2)).strip()
                heap_sections.append(heap)

        return heap_sections

    def extract_heaps(self):
        self.extract_main_heap()
        regions = self.extract_heap_info()

        if len(regions) != 0:
            for r in regions:
                memory = gdb.parse_and_eval(
                    "*(struct _heap_info*) {}".format(r.start))
                ss = str(memory['ar_ptr']).strip()
                if ss in state_manager.arenas:
                    r.ar_add = str(memory['ar_ptr'])
                    r.offset = str(memory['pad']).strip('"')
                    r.size = int(str(memory['size']) )
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

    def extract_main_heap(self):
        main_heap = MemRegion()
        main_heap.start = gdb.execute(
            'p mp_.sbrk_base',
            to_string=True).strip().split(' = ')[1].strip('"')
        main_heap.end = str(gdb.parse_and_eval("(void *) sbrk(0)"))
        total = int(main_heap.end, 16) - int(main_heap.start, 16)
        main_heap.size = total
        main_heap.ar_add = state_manager.arenas[0]
        main_heap.is_main = True
        main_heap.offset = main_heap.start
        state_manager.arena2heaps[main_heap.ar_add] = [0]
        state_manager.heaps.append(main_heap)

    def invoke(self, arg, from_tty):
        table_width = 100
        state_manager.heaps = []
        state_manager.arena2heaps = {}
        self.extract_heaps()
        inferior = gdb.selected_inferior()
        cnt = 0
      
        for ar in state_manager.arenas:
            if len(state_manager.arena2heaps[ar]) > 0:
                for heap_indx in state_manager.arena2heaps[ar]:
                    tmp_heap = state_manager.heaps[heap_indx]
                    end = int(tmp_heap.end, 16)
                    start = int(tmp_heap.offset, 16)
                   
                    PrettyPrinter.print_header(
                        "analysis thread's heaps", width=table_width)
                    
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
                    
                    self.count_memory_usage(inferior, start, end)

        PrettyPrinter.print_footer(100)