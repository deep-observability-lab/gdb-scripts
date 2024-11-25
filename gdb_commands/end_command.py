from ssh_utils import SSHConnection
import gdb
import os
import time
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)


class ExitCommand(gdb.Command):
    def __init__(self):

        super(
            ExitCommand,
            self).__init__(
            "exit_gdb",
            gdb.COMMAND_SUPPORT,
            gdb.COMPLETE_NONE,
            True)
        self.username = None
        self.password = None

        try:
            # Use `info target` to gather connection details
            target_info = gdb.execute('info target', to_string=True)
            if "Remote serial target" in target_info:
                self.ip = gdb.execute(
                    'show environment IP_ADDRESS',
                    to_string=True).strip().split(' = ')[1]
                self.username = gdb.execute(
                    'show environment USERNAME',
                    to_string=True).strip().split(' = ')[1]
                self.password = gdb.execute(
                    'show environment PASSWORD',
                    to_string=True).strip().split(' = ')[1]
            else:
                self.ip = None

        except gdb.error as e:
            print("Error fetching details from target: {}".format(e))
            self.ip = None

    def invoke(self, arg, from_tty):
        try:
            if self.ip is not None:
                print("detach from the process ")
                ssh_conn = SSHConnection(
                    ip=self.ip,
                    username=self.username,
                    password=self.password)
                gdb.execute("detach")
                time.sleep(2)
                ssh_conn.connect()
                gdbserver_command = 'echo "{}" | sudo -S pkill gdbserver'.format(
                    self.password)
                if self.username == "root":
                    gdbserver_command = 'pkill gdbserver'
                output, error = ssh_conn.run_command(gdbserver_command)
                print("killing gdbserver process on remote...")
                time.sleep(2)
            print("exit from gdb local")
            time.sleep(2)
            gdb.execute("q")
        except Exception as e:
            print("Error while SSH to destination: {}".format())
        finally:
            ssh_conn.close()
