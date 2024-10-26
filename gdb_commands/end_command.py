import gdb
import paramiko
import os
import time

class SSHManager(gdb.Command):
    def __init__(self):
        # Retrieve environment variables
        super (SSHManager, self).__init__("exit_gdb", gdb.COMMAND_SUPPORT,gdb.COMPLETE_NONE,True)
        self.ip = gdb.execute('show environment IP_ADDRESS', to_string=True).strip().split(' = ' )[1] 
        self.username = gdb.execute('show environment USERNAME', to_string=True).strip().split(' = ')[1]
        self.password = gdb.execute('show environment PASSWORD', to_string=True).strip().split(' = ')[1]
       # self.tmp_file_path = gdb.execute('show environment TEMP_PATH' , to_string=True).strip().split(' = ')[1]

    def invoke(self,arg , from_tty):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            print("detach from the process " ) 
            gdb.execute("detach")
            time.sleep(2)
            ssh.connect(self.ip, username=self.username, password=self.password, timeout=5)
            stdin, stdout, stderr = ssh.exec_command("pkill gdbserver")
            # Print stdout and stderr for debugging
            print( "killing gdbserver process on remote...")
            time.sleep( 2) 
            print("exit from gdb local" ) 
            time.sleep(2) 
            gdb.execute("q")
        except Exception as e:
            print(f"Error while SSH to destination: {e}")
        finally:
            ssh.close()


# Call the function
SSHManager()

