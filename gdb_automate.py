import os
import subprocess
from ssh_utils import SSHConnection
from config import SYSROOT_PATH

    
def check_port(ssh_conn ):
    ports_list = [ 4554 , 5566 , 1343 ] 
    ssh_conn.connect()
    gdbserver_command = f"netstat -tunlp | grep gdbserver | awk '{{print $4}}' | cut -d ':' -f2"
    output, _ = ssh_conn.run_command(gdbserver_command)
    output = output.strip()
    ports = output.splitlines()
    for p in ports_list :
        if not (str(p) in ports) :
            print("port : " , p )
            return p
    return 0

def is_stripped(binary_path):
    """Check if the binary is stripped or not."""
    if not os.path.isfile(binary_path):
        print(f"Error: The path '{binary_path}' is not a valid file.")
        return None
    try:
        command = f"file {binary_path}"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
        # If the output contains symbol table entries, the binary is not stripped
        if "not stripped" in output:
            return False  # Not stripped
        elif "stripped" in output :
            return True
        else:
            return False  # Stripped
    except subprocess.CalledProcessError as e:
        print(f"Error while executing readelf: {e.output.decode()}")
        exit()


def extract_shared_libs(ip, username, password , pid , rel):
    """
        get the sharedlibrary names, which runnig process using them. in some cases gdb only looking for the symlinks, 
        so , creating the symlink at the path gdb would expect them to be, helps to correctly debug the process. 
    """
    libs_path = ''
    try:
        ssh_conn = SSHConnection(host=ip, username=username, password=password)
        ssh_conn.connect()
        command = f"cat /proc/{pid}/maps | grep '\\.so' | awk -F'/' '{{print $NF}}' | sort -u"
        stdout , _ = ssh_conn.run_command(command=command)
        result = stdout.strip()
        non_stripped = {}
        if result:
            list_libs = result.split()
            
            for i in range(len(list_libs)): 
                find_command = f"find {SYSROOT_PATH} -type f -name '{list_libs[i]}'"
                paths = subprocess.check_output(find_command, shell=True).decode().strip()
                if paths:
                    splited_pathes = paths.split()
                    for p in splited_pathes :
                        if is_stripped(p)==False:
                            token  = p.split('/')
                            lib_name = token[ len(token)-1 ] 
                            non_stripped[lib_name] = p  
                            libs_path += p.replace(list_libs[i] , '')
                            if i != len(list_libs ) -1 :
                                libs_path += ':'
                            break
                else:
                    print("No paths found.")
        else:
            print("No shared libraries found.") 
     
        sym_link = "find /lib/ /usr/lib/ -type l -name \"*.so.*\""
        stdout , _ = ssh_conn.run_command( sym_link)
        sym_links = stdout.strip().split()
    
        for link in sym_links : 
            command = f"readlink -f {link} | awk -F'/' '{{print $NF}}'" 
            stdout , _ = ssh_conn.run_command(command)
            real_lib = stdout.strip()    
            if real_lib in non_stripped.keys(): 
                tmp = non_stripped[real_lib ]         
                libs_path.replace( tmp+':' , '' )
                ll = SYSROOT_PATH + f'{rel}' + link 
                os.symlink( tmp  , ll )
    except Exception as e:
        print(f"Error: {e}")
        exit()
    finally:
        ssh_conn.close()
        return libs_path.strip().replace('\n' , ':')


def run_gdb_local(app, ip, port, pid, user, pwd, rel, arch="powerpc:common"):
    import tempfile
    binary_path = SYSROOT_PATH+f'{rel}/'  + f"app/{app}"

    SUBLIBS = extract_shared_libs(ip, user, pwd , pid,rel )    
    tmp_file_path = ''
   # print("subdirs ***** : " ,  SUBLIBS ) 
    curr_dir = os.getcwd() 
    gdb_commands = f"""
set sysroot {SYSROOT_PATH} 
dir {SYSROOT_PATH}
set solib-search-path {SUBLIBS}
set architecture {arch}
set environment IP_ADDRESS={ip}
set environment USERNAME={user}
set environment PASSWORD={pwd}
python
import sys
sys.path.append(f"{curr_dir}/gdb_commands/")
sys.path.insert(0, '../env/lib/python3.8/site-packages/')
import end_command 
end
source __init__.py
target extended-remote {ip}:{port}
attach {pid}
list
"""
    # Create a temporary file for the GDB commands
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.gdb') as tmp_file:
        tmp_file.write(gdb_commands)
        tmp_file_path =   tmp_file.name

    try:
        
        gdb_c =  f'gnome-terminal -- gdb-multiarch -x {tmp_file_path} {binary_path}'
        process = subprocess.Popen( gdb_c , shell = True )
        process.wait()
    except Exception :
        print("")
    

def run_gdbserver(user, ip, pwd, port=1234):
    ssh_conn = SSHConnection(host=ip, username=user, password=pwd)
    port = check_port( ssh_conn )  
    if port == 0 : 
        print( " all ports for gdbserver are busy " ) 
        exit() 
    try:
        ssh_conn.connect()
        gdbserver_command = f"gdbserver --multi :{port}"
        ssh_conn.run_command(gdbserver_command)
    finally:
        ssh_conn.close()
    return port


# def main(argv):
#     parser = argparse.ArgumentParser(description='connect to gdbserver on remote and\nattach one process on special port.')
#     parser.add_argument('-ip' , '--ip' ,type=str , required=True , help='ip address of remote board (e.g. 192.168.5.5)' )
#     parser.add_argument('-u' , '--username' , type=str , required=True , help='username on the remote board (e.g. root)')
#     parser.add_argument('-pid', '--process_id', type=str, required=True, help='Process ID (e.g. 1234)')
#     parser.add_argument('-password' , '--password' ,type=str , required=True , help='password for authentication on remote board.' )
#     parser.add_argument("-app" , "--application" , type=str , required=True , help="name of binary debugging process is belong.")
#     parser.add_argument("-arch" , "--architecture" , type=str , required=False , help="architecture set for cross-compiled binary, powerpc:common is the default architecture.")
#     args = parser.parse_args()
#     port = run_gdbserver(user=args.username , pwd=args.password , ip= args.ip)
#     run_gdb_local(app=args.application, port = port , pid=args.process_id , rel=args.release, user=args.username , pwd=args.password, ip= args.ip , arch = args.architecture )

# if __name__ == "__main__":
#     import sys
#     main(sys.argv[1:])

