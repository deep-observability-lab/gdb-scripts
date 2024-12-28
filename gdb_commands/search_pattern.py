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


# Function to search for the pattern in memory
def search_pattern(start_addr, pattern , byte_num):
    # Convert start address and pattern into integers
    start_addr = start_addr
    pattern = bytes.fromhex(pattern)
    print( "start searching at : " , hex(start_addr ))
    print("pattern : " , pattern )
    current_addr = start_addr
    pre = ''
    while True:
        try:
            # Read memory from current address with buffer size
            mem = gdb.execute(f'x/{byte_num}bx {current_addr}', to_string=True).split(":")[1]
            striped = mem.strip().replace(' ', '').replace('\n', '')
            
            hex_values = re.findall(r'0x[0-9a-fA-F]+', mem)

            # Step 2: Remove the '0x' prefix and join the hex values
            striped = ''.join(value[2:] for value in hex_values)

            # Step 3: Convert the hex string to bytes
            #print("byte data : " , striped  )    
            byte_data = bytes.fromhex(striped)
            # Check if the pattern is found in the read memory
        
            if pattern in byte_data:
                print(f'Pattern found at address: 0x{current_addr:08x}')
                break
            pre = current_addr
            #print("address : " , hex(pre ))
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
    pattern = "9421ffe0" #sys.argv[2]
    start_addresses = get_memory_ranges()
    byte_num = 4 
    for address in start_addresses : 
    # Run the pattern search function
        search_pattern( address, pattern , byte_num)
    

# Execute main function when the script is loaded in GDB
if __name__ == "__main__":
    main()


