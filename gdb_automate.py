"""
This module provides functions to manage gdbserver through SSH connections.

It includes capabilities to check available ports for gdbserver, 
run GDB locally with specific parameters, retrieve the program name 
from gdbserver, and execute gdbserver on a specified port. 

Functions:
- check_port: Determines an available port for gdbserver.
- run_gdb_local: Executes GDB locally with the specified application, IP, port, PID, user, and password.
- get_program_name: Retrieves the name of the program associated with a given PID from the gdbserver.
- run_gdbserver: Starts gdbserver on a specified port using SSH connection.
"""

import os
import subprocess
import tempfile
import sys
import site
from ssh_utils import SSHConnection
import config as cnf


def check_port(ssh_conn, password, username):
    """Check available ports for gdbserver."""
    ssh_conn.connect()
    command = (
        'echo "{}" | sudo -S netstat -tunlp | '
        'grep gdbserver | awk \'{{print $4}}\' | cut -d \':\' -f2'
    ).format(password)
    if username == 'root':
        command = (
            'netstat -tunlp | grep gdbserver | '
            'awk \'{{print $4}}\' | cut -d \':\' -f2'
        )

    output, _ = ssh_conn.run_command(command)
    ports = output.strip().splitlines()

    for p in cnf.AVAILABLE_PORTS:
        if str(p) not in ports:
            return p
    return 0


def run_gdb_local(app, ip, port, pid, user, pwd, arch="auto"):
    """Run gdb locally with specified parameters."""
    if arch == None : 
        arch = "auto"
    binary_path = os.path.join(cnf.WORKSPACE, app)
    python_path = sys.executable
    site_package = site.getsitepackages()[0]
    gdb_commands = """
# set auto-solib-add on
set sysroot {}
set solib-search-path {}
set architecture {}
set environment IP_ADDRESS={}
set environment USERNAME={}
set environment PASSWORD={}
python
import sys
import os
import site
sys.executable = "{}"
sys.path.insert(0, "{}")
sys.path.append(os.path.join(os.getcwd(), "gdb_commands/"))
import end_command
end
source gdb_commands/__init__.py
target extended-remote {}:{}
attach {}
""".format(cnf.WORKSPACE, cnf.WORKSPACE, arch, ip, user, pwd, python_path, site_package, ip, port, pid)

    # Create a temporary file for the GDB commands
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.gdb') as tmp_file:
        tmp_file.write(gdb_commands)

    try:
        gdb_command = (
            'gnome-terminal -- gdb-multiarch -x {} {}'
        ).format(tmp_file.name, binary_path)

        process = subprocess.Popen(gdb_command, shell=True)
        process.wait()
    except subprocess.SubprocessError as e:
        print("Error starting gdb: {}".format(e))


def get_program_name(user, ip, pwd, pid):
    """Get the program name from the gdbserver using SSH."""
    ssh_conn = SSHConnection(ip=ip, username=user, password=pwd)
    program = ''
    try:
        ssh_conn.connect()
        gdbserver_command = 'ps -p {} -o comm='.format(pid)
        program, _ = ssh_conn.run_command(gdbserver_command)
    finally:
        ssh_conn.close()
    return program


def run_gdbserver(user, ip, pwd, port=4554):
    """Run gdbserver on the specified port."""
    ssh_conn = SSHConnection(ip=ip, username=user, password=pwd)
    port = check_port(ssh_conn, pwd, user)

    if port == 0:
        print("All ports for gdbserver are busy or connection cannot be established.")
        exit()

    print("gdbserver listening on port {}".format(port))
    try:
        ssh_conn.connect()
        command = (
            'echo "{}" | sudo -S gdbserver --multi :{} > '
            '/dev/null 2>&1 &'
        ).format(pwd, port)
        if user == "root":
            command = 'gdbserver --multi :{} > /dev/null 2>&1 &'.format(port)

        ssh_conn.run_command(command)
    finally:
        ssh_conn.close()
    return port
