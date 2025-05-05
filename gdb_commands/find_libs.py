import gdb
import re
import ast
from ssh_utils import SSHConnection
import os

class GetSharedLibraries(gdb.Command):
    """Extract specific shared library paths from 'info sharedlibrary' command.
    
    Usage:
        get_shared_libs lib1 lib2 ...
    """
    def __init__(self):
        super(GetSharedLibraries, self).__init__("get_shared_libs", gdb.COMMAND_USER)
        self.username = None
        self.password = None

        try:
            # Use `info target` to gather connection details
            target_info = gdb.execute('info target', to_string=True)
            
            # if "remote target" in target_info.lower():
            self.ip = gdb.execute(
                'show environment IP_ADDRESS',
                to_string=True).strip().split(' = ')[1]
            self.username = gdb.execute(
                'show environment USERNAME',
                to_string=True).strip().split(' = ')[1]
            self.password = gdb.execute(
                'show environment PASSWORD',
                to_string=True).strip().split(' = ')[1]
            # else:
            #     self.ip = None

        except (gdb.error, IndexError, KeyError, ValueError) as e:
            # print(f"Error fetching details from target: {e}")
            self.ip = None

    def invoke(self, arg, from_tty):
        if not arg:
            print("Usage: get_shared_libs lib1 lib2 ...")
            return
        # Convert input argument string to a list of library names
    
        actual_dict = ast.literal_eval(arg)

        # Run GDB command
        output = gdb.execute("info sharedlibrary", to_string=True)
       
        # Regular expression to capture library paths
        solib_search_path = set()

        lib_paths = re.findall(r'/[^\s]+', output)
        try: 
            ssh = SSHConnection(
                        ip=self.ip,
                        username=self.username,
                        password=self.password)  
            ssh.connect() 
            for link in lib_paths:
                
                command = "echo readlink -f {} | awk -F'/' '{{print $NF}}'" .format(
                    link)
                if self.username != "root":
                    command = "echo '{}' | sudo -S readlink -f {} | awk -F'/' '{{print $NF}}'".format( self.password , link )
                stdout, stderr = ssh.run_command(command)
                
                real_lib = stdout.strip()
                
                if real_lib in actual_dict.keys():
                    lib_base_dir =  '/'.join ( actual_dict[real_lib].split('/')[:-1]) 
                    sym_link = lib_base_dir +'/'+ link.split('/')[-1]
                    if not os.path.exists(sym_link):
                        try:
                            os.symlink(actual_dict[real_lib], sym_link)
                        except FileExistsError:
                            print(f"Symlink already exists: {sym_link}, skipping.")
                    else:
                        print(f"Symlink already exists: {sym_link}, skipping.")
                    solib_search_path.add( lib_base_dir)
            if len(solib_search_path) > 0 : 
                gdb.execute("set solib-search-path {}".format( ':'.join(solib_search_path) )  )

        except Exception as e : 
            print("Error while SSH to destination: {}".format(e))
        finally:
            ssh.close()
        
            