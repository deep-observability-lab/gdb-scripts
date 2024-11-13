import gdb
from global_state import state_manager , SYSTEM , HEAPINFO_SIZE , ARENA_SIZE

class MemRegion() : 
    def __init__(self):
        self.start= ''
        self.end = ''
        self.size = 0 
        self.offset = 0x00
        self.is_main = False
        self.ar_add= ''
        self.is_first = False

    def __str__(self) -> str:
        strr = "starts at: " + self.start + ' , ' + "ends at: "+self.end + " with arena: " + self.ar_add + " and size " + str(self.size)
        
        if self.is_main : 
            return "Main heap :\n\t" + strr
        return strr
     
class Heap( gdb.Command ):
    def __init__(self ) : 
        super( Heap ,self ).__init__( "heap", gdb.COMMAND_USER)
        print( " init (((#939 " ) 
    def count_memory_usage(self, inferior , heap_start , heap_end):
        allocated = 0
        total = heap_end - heap_start
     
        cur = heap_start
        nxhdr = 0 
        while(cur != heap_end ) : 
            num_words = 1
            memory = inferior.read_memory(cur+ SYSTEM ,num_words * 4)
           
            word = memory[0:4]
            value = int.from_bytes(word, byteorder='big')
          #  print(f"0x{cur + 0:x}: 0x{value:08x}")
            sz = value & ~0x7
           # print( " this is size for debug :  " , sz ) 
           # print(f"current address chunk : {hex(cur)} with size of {hex(sz)} bytes")
            nxhdr = cur + sz
            if (nxhdr == heap_end) : 
                break
            memory = inferior.read_memory(nxhdr + SYSTEM ,num_words * 4)
            word = memory[0:4]
            value = int.from_bytes(word, byteorder='big')

            pbit = (value & 0x1)
            # Determine if the block is allocated or freed
            if pbit == 1:
               # print("Allocated")
                allocated += sz
            else:
               # print("Freed")
                pass
            cur = nxhdr

        print(f"{allocated} of {total} is allocated.")
        

    def extract_heap_info(self):
        is_heap = False
        mappings_output = gdb.execute("info proc mappings" , to_string=True)
        heap_sections = []
        lines = mappings_output.splitlines()

        for line in lines:
            
            parts = line.split() 
            if len(parts) ==  5  :
                heap = MemRegion()
                heap.start = str(parts[0]).strip()
                heap.end = str(parts[1]).strip()
                heap.size = int(str(parts[2]), 16)
                heap_sections.append(heap)

        return heap_sections
    
    def extract_heaps(self ):
        
        self.extract_main_heap()
        regions = self.extract_heap_info()  
        regions.pop(0)
    
        for r in regions: 
            memory = gdb.parse_and_eval( f"*(struct _heap_info*) {r.start}")
            ss = str(memory['ar_ptr']).strip()
        
            if (ss in state_manager.arenas) : 
                r.ar_add = str(memory['ar_ptr'])
                if (str(memory['prev']) == '0x0'): 
                    r.is_first = True
                if r.ar_add not in state_manager.arena2heaps.keys(): 
                    state_manager.arena2heaps[r.ar_add] = []
                state_manager.arena2heaps[r.ar_add].append(len(state_manager.heaps))
                state_manager.heaps.append(r)
                #print(str(r))
            #else : 
                #print(f'')
        for ar in state_manager.arenas  : 
            if not ( ar in state_manager.arena2heaps.keys() ) : 
                state_manager.arena2heaps[ar ] = [] 
    
    def print_thread_heaps(self , heaps ) : 
        if len(heaps) > 0 : 
            print("thread heaps: ")
            for i in range(len(heaps)) : 
                print(type(heaps[i]))
                if i ==0 : 
                    print(f"Main Heap: \n\t" + str(heaps[i]))
                else : 
                    print(str(heaps[i]))

    def extract_main_heap(self) : 
        main_heap = MemRegion()
        main_heap.start = gdb.execute('p mp_.sbrk_base', to_string=True).strip().split(' = ')[1].strip('"')  
        main_heap.end = str(gdb.parse_and_eval("(void *) sbrk(0)"))
        total =  int(main_heap.end  , 16)- int(main_heap.start ,16)
        main_heap.size = total
        main_heap.ar_add = state_manager.arenas[0]
        main_heap.is_main = True
        state_manager.arena2heaps[main_heap.ar_add] = []
        state_manager.arena2heaps[main_heap.ar_add].append(0)
        state_manager.heaps.append(main_heap)
        
    def invoke( self , arg , from_tty ):
        state_manager.heaps = []
        state_manager.arena2heaps = {}
        self.extract_heaps() 
        inferior= gdb.selected_inferior()
        print(" arenas " ,  state_manager.arenas ) 
        for ar in state_manager.arenas: 
            if len ( state_manager.arena2heaps[ar] ) > 0 : 
            
                for heap_indx in state_manager.arena2heaps[ar] : 
                    tmp_heap = state_manager.heaps[heap_indx]
                    end = int(tmp_heap.end, 16)
                    start = int(tmp_heap.start,16)
                    if tmp_heap.is_first and not tmp_heap.is_main: 

                        start += ARENA_SIZE + HEAPINFO_SIZE
                    elif not tmp_heap.is_first and not tmp_heap.is_main : 
                    
                        start +=  HEAPINFO_SIZE
                    else : 
                        print("******************* analysis thread heaps *******************")
   
                    print("analysis heap : \n" , str(tmp_heap))
                    self.count_memory_usage(inferior , start , end)

                bins = gdb.parse_and_eval(f"(*(struct malloc_state*) {ar}).bins")
                length = bins.type.sizeof // bins.type.target().sizeof
                print(f"arena.bins length: {length}")
            

