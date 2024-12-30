import gdb
import sys
import re
import time 
# Function to convert a hexadecimal string to an integer
def hex_to_int(hex_str):
    return int(hex_str, 16)


def get_memory_ranges():
    """Get the starting addresses of memory ranges from the 'info files' command."""
    try:
        # Execute the 'info files' command and get the output
        output = gdb.execute("info files", to_string=True)
        
        # Use a regular expression to find memory ranges
        memory_ranges = re.findall(r'0x([0-9a-fA-F]+) - 0x[0-9a-fA-F]+', output)
        
        # Convert the found addresses to integers and return them as a list
        start_addresses = [int(f'0x{addr}', 16) for addr in memory_ranges]
        return start_addresses

    except gdb.error as e:
        print(f"Error executing GDB command: {e}")
        return []


def read_memory( address , size_to_read , byte_order ):
        inferior = gdb.selected_inferior()
        memory = inferior.read_memory(
            address , size_to_read)
        # word = memory[0:4]
        value = int.from_bytes(memory , byteorder=byte_order)
        return value

def search_pattern(start_addr, pattern , byte_num):
   
    pattern = str(pattern)
    print( "start searching at : " , hex(start_addr ))
    print("pattern : " , pattern )
    current_addr = start_addr
    size_of_char = gdb.lookup_type("char").pointer().target().sizeof
    if byte_num < size_of_char : 
        print( "number of byte to read is less than char size.")
        return

    byte_order = gdb.execute("show endian", to_string=True)
    if "little" in byte_order:
        byte_order = 'little'
    elif "big" in byte_order:
        byte_order = 'big'

    pre = ''
    while True:
        try:
           
            mem = read_memory(current_addr, byte_num, byte_order)   
            if pattern in str(mem):
                print(f'Pattern found at address: 0x{current_addr:08x}')
                break
            pre = current_addr
            # Move to the next memory chunk
            current_addr += byte_num
        
        except gdb.error as e:
            # If we cannot access memory, break the loop
            print(f'Error accessing memory at address: 0x{current_addr:08x}')
            if pre : 
                print("last address to read " ,hex( pre)  )
            break
    print("------------------------------------------------------------------------------------------")

def main():

    #start_address = "0f6bc844"#"0f614d54"  #sys.argv[1]
    pattern = "0x9421ffe0" #sys.argv[2]
    hex_digits = pattern[2:]  # '9421ffe0'
    byte_num  = len(hex_digits) // 2
    start_addresses = get_memory_ranges()
    for address in start_addresses : 
        search_pattern( address, pattern , byte_num)
    

# Execute main function when the script is loaded in GDB
if __name__ == "__main__":
    main()


