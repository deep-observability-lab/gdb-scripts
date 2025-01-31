import gdb
import re
from gdb_commands.global_state import state_manager
from pretty_print import PrettyPrinter

label_color = PrettyPrinter.LABEL_COLOR
reset_color = PrettyPrinter.RESET_COLOR


class SearchPatternCommand(gdb.Command):
    """Search for a pattern in memory within the mapped memory ranges.
    
    Usage: search_pattern <pattern>
    - <pattern>: The pattern to search for (e.g., 0xb5e00050)
    """

    def __init__(self):
        super(SearchPatternCommand, self).__init__("search_pattern", gdb.COMMAND_DATA)

    def hex_to_int(self, hex_str):
        """Convert a hexadecimal string to an integer."""
        return int(hex_str, 16)

    def get_memory_ranges(self):
        """Get memory ranges from the 'info files' command as pairs of (start, end) addresses."""
        try:
            output = gdb.execute("info files", to_string=True)
            
            memory_ranges = re.findall(
                r'0x([0-9a-fA-F]+) - 0x([0-9a-fA-F]+)', output)
        
            address_pairs = [(self.hex_to_int(start), self.hex_to_int(end)) 
                            for start, end in memory_ranges]            
            return address_pairs

        except gdb.error as e:
            PrettyPrinter.print_error(f"Error executing GDB command: {e}")
            return []
        
    def read_memory(self, address, size_to_read, byte_order):
        """Read memory from the given address."""
        inferior = gdb.selected_inferior()
        memory = inferior.read_memory(address, size_to_read)
        value = int.from_bytes(memory, byteorder=byte_order)
        return value

    def search_pattern(self, start_addr, end_addr, pattern, byte_num):
        """Search for the pattern between the given start and end addresses."""
        
        pattern = str(hex(int(pattern, 16)))
        
        end_addr = int(end_addr, 16)
        current_addr = int(start_addr, 16) 
        size_of_char = gdb.lookup_type("char").pointer().target().sizeof
        
        if byte_num < size_of_char:
            PrettyPrinter.print_error("Number of bytes to read is less than the size of a char.")
            return
        byte_order = gdb.execute("show endian", to_string=True)
        byte_order = 'little' if "little" in byte_order else 'big'
        pre = None
        while current_addr < end_addr:
            try:
                if current_addr + byte_num > end_addr:
                    break

                mem = self.read_memory(current_addr, byte_num, byte_order)    
                
                if pattern in str(hex(mem)):
                    PrettyPrinter.print_half_header(f"Pattern found at address: 0x{current_addr:08x}", PrettyPrinter.YELLOW_COLOR)
                    break
                pre = current_addr
                current_addr += byte_num
            except gdb.error:
                PrettyPrinter.print_error(f"Error accessing memory at address: 0x{current_addr:08x}")
                if pre:
                    PrettyPrinter.print_row("Last address read", hex(pre))
                break
    
    def invoke(self, arg, from_tty):
        """Command invocation logic."""
        args = arg.split()
        
        if not args:
            PrettyPrinter.print_error("Usage: search_pattern <start_address> <end_address> <pattern> OR search_pattern <pattern>")
            return

        if len(args) == 1:
            pattern = args[0].strip()
            if not pattern.startswith("0x"):
                PrettyPrinter.print_error("Pattern must be in hexadecimal format (e.g., 0xb5e00050).")
                return

            hex_digits = pattern[2:]
            byte_num = len(hex_digits) // 2
            PrettyPrinter.print_header("Searching for Pattern")
            PrettyPrinter.print_row("Pattern", pattern)
            
            start_addresses = self.get_memory_ranges()
            for start, end in start_addresses:
                self.search_pattern(str(hex(start)), str(hex(end)), pattern, byte_num)
            PrettyPrinter.print_footer()

        elif len(args) == 3:
            start_address, end_address, pattern = map(str.strip, args)

            if not (start_address.startswith("0x") and end_address.startswith("0x") and pattern.startswith("0x")):
                PrettyPrinter.print_error("Addresses and pattern must be in hexadecimal format (e.g., 0xb5e00050).")
                return

            hex_digits = pattern[2:]
            byte_num = len(hex_digits) // 2
            PrettyPrinter.print_header("Searching for Pattern")
            PrettyPrinter.print_row("Pattern", pattern)
            
            self.search_pattern(start_address, end_address, pattern, byte_num)
            PrettyPrinter.print_footer()
        else:
            PrettyPrinter.print_error("Error: This command requires either 1 argument (pattern) or 3 arguments (start_address, end_address, pattern).")
            return