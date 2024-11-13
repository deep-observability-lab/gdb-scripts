import gdb
from global_state import state_manager 

class Bins( gdb.Command ):
    def __init__(self ) : 
        super( Bins ,self ).__init__( "bins", gdb.COMMAND_USER)
        
    # check the head of small / large / unsorted bins and follow the chunks. get the chunk count.
    def get_head(self , indx , ar_add) :
        if indx == 0 : 
            return 0
        bin_head = gdb.parse_and_eval(f"( *(struct malloc_state*) {ar_add}).bins[{indx *2-2}]")#int(str(self.bins[indx]).split()[0
        #print( f"the head of bin at index {indx} is {bin_head}")
        return bin_head
    
    def walk_doubled_link_bin_at(self , index , name , bin_head) : 
        if bin_head == 0 : 
            return
        cur = str(bin_head).split()[0]
        bin_head = cur
        pre = cur
        num_chunks =0
        while(True): 
            mchunkptr = gdb.parse_and_eval(f"*(mchunkptr) {cur}" )
            fd = str(mchunkptr['fd']).split()[0]
            bk = str(mchunkptr['bk']).split()[0]
            if num_chunks == 0 : 
                pre = bk 
            #print(f"fd : {fd} bk: {bk} head : {cur} , pre : {pre}")
            if fd == bin_head :
                # circule
                break
            num_chunks +=1
            if bk != pre : 
                print(f"corruption at {name} bin with index: {index}")
                exit(1)  
            pre = cur
            cur = fd

        if num_chunks != 0  : 
            print(f"the number of chunks in {name} bin at bins.index: {index} is {num_chunks}")
        #else : 
        #    print(f"bin at bins.index: {index} is empty")

    def walk_single_link_bin_at(self , index , name , bin_head) : 
        if bin_head == 0 : 
            return
        cur = str(bin_head).split()[0]
        bin_head = cur
        num_chunks =0
        while(True): 
            mchunkptr = gdb.parse_and_eval(f"*(mchunkptr) {cur}" )
            fd = str(mchunkptr['fd']).split()[0]
            #print(f"fd : {fd} bk: {bk} head : {cur}")
            if fd == bin_head :
                break
            num_chunks +=1
            cur = fd

        if num_chunks != 0  : 
            print(f"the number of chunks in {name} bin at bins.index: {index} is {num_chunks}")
        #else : 
        #    print(f"bin at fastbinsY.index: {index} is empty")

    def walk_unsorted_bin(self , ar_add) : 
        print("******** walking unsorted bin : ")
        bin_head = self.get_head(1, ar_add)
        self.walk_doubled_link_bin_at(1, 'unosrted' , bin_head)
        
    def walk_fast_bin(self , ar_add) : 
        print("******** walking fast bin : ")
        for i in range(10) : 
            fbin_head = gdb.parse_and_eval(f"( *(struct malloc_state*) {ar_add}).fastbinsY[{i}]")
            if fbin_head == 0:
                print(f"Fastbin[{i}] is empty")
                continue
            cur = str(fbin_head).split()[0]
            num_chunks = 0
            while cur != "0x0":  # Continue until fd points to NULL
                try:
                    mchunkptr = gdb.parse_and_eval(f"*(mchunkptr) {cur}")
                    fd = str(mchunkptr['fd']).split()[0]
                    num_chunks += 1
                    print(f"Chunk {num_chunks}: Address = {cur}, Size = {mchunkptr['size']}")
                    cur = fd

                except gdb.MemoryError:
                    print(f"Cannot access memory at address {cur}, stopping.")
                    break

            if num_chunks != 0:
                print(f"Fastbin[{i}] has {num_chunks} chunks.")
            #else:
            #    print(f"Fastbin[{i}] is empty")

    def walk_small_bins(self , ar_add) : 
        print("******** walking small bin : ")
        #size small bin
        for i in range(2 , 64) : 
            bin_head = self.get_head(i,ar_add)
            self.walk_doubled_link_bin_at(i , 'small bin',bin_head)

    def walk_large_bins(self,ar_add) : 
        print("******** walking large bin : ")
        for i in range(64 , 127) : 
            bin_head = self.get_head(i,ar_add)
            self.walk_doubled_link_bin_at( i, 'large bin' , bin_head)

    def invoke( self , arg , from_tty ):    
        state_manager.bins = []
        for ar in state_manager.arenas: 
            print( "scan bins for arena : " , ar ) 
            if len ( state_manager.arena2heaps[ar] ) > 0 : 
                self.walk_fast_bin(ar)
                self.walk_unsorted_bin(ar)
                self.walk_small_bins(ar)
                self.walk_large_bins(ar)
