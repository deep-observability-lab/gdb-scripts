import gdb

class FindStr(gdb.Command):
    """
    Command to search for a given hex string in a specified memory range.
    
    Usage: find_str <start_address> <end_address> <hex_content>
    Example: find_str 0x400000 0x500000 68656c6c6f
    This will search for the hex string "68656c6c6f" (which is "hello" in ASCII) in the memory range.
    """
    def __init__(self):
        super(FindStr, self).__init__("find_str", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) != 3:
            print("Usage: find_str <start_address> <end_address> <hex_content>")
            return

        start_addr = int(args[0], 16)
        print("start  " , start_addr) 
        end_addr = int(args[1], 16)
        hex_content = args[2]
    
        # Convert hex string to byte array
        content_bytes = bytes.fromhex(hex_content)
        content_length = len(content_bytes)
    
        # Iterate over the memory range
        addr = start_addr
        while addr <= end_addr - content_length:
            try:
                # Read memory at current address
                mem = gdb.inferiors()[0].read_memory(addr, content_length)
                fdsfsford = mem[0:4]
                value = int.from_bytes(word  , byteorder='big')
                if value  == int( hex_content , 16 ) :
                    print(f"Found match at address: {hex(addr)}")
                    break 
            except gdb.MemoryError:
                # Skip unreadable regions
                pass

            addr += 4

        print("Search completed.")

# Register the command with GDB
FindStr()

