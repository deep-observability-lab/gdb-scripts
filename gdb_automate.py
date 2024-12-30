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
import re
from launch_json_generator import generate_debug_config
import shutil

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


def extract_shared_libraries_from_core(core_dump_path):
    """Extracts shared libraries from a core dump using readelf and filters paths ending in .so."""
    try:
        # Run readelf to get all information, then filter for .so files
        readelf_output = subprocess.run(
            ["readelf", "-a", core_dump_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Extract .so paths using regex
        so_paths = []
        for line in readelf_output.stdout.splitlines():
            match = re.search(r"(/.+\.so(?:\.[\d]+)*)", line)
            if match:
                lib = match.group(1).split('/')[-1]
                so_paths.append(lib)
        return so_paths

    except subprocess.CalledProcessError as e:
        print("Error running readelf: {}".format(e))
        return {}


def check_libraries_in_path(core_dump_path, search_path):
    """Checks how many shared libraries exist in the given path."""
    found = []
    not_found = []
    libraries = extract_shared_libraries_from_core(core_dump_path)

    for lib in libraries:
        lib_path = os.path.join(search_path, lib)
        if os.path.exists(lib_path):
            found.append(lib)
        else:
            not_found.append(lib)
    result = False
    if len(not_found) > 0:
        print("Following libraries were not found in workspace.")
        for lib in not_found:
            print("  - {}".format(lib))
        cont = input("[1] Continue with whatever libraries found in workspace.\n"
                     "[2] use libraries in default path in local system: /lib /usr/lib /lib64 /usr/lib64\n"
                     "[3] exit program.\n")
        if cont == "3":
            print("Exit.")
            exit(0)  # Exit with success code
        elif cont == "1":
            print("Continuing with the libraries at workspace.")
            result = True
        elif cont == "2":
            print("Using libraries in the default path in the local system.")
        else:
            print("Invalid input. Exiting the program.")
            exit(1)  # Exit with error code

    return found, result


def create_gdbcommand(arch, user, pwd, ip, port, pid,
                      binary_path ,is_live=True, core_file=None,ui_mood='gdb'):
    python_path = sys.executable
    site_package = site.getsitepackages()[0]
    solib_path = cnf.WORKSPACE
    sysroot = cnf.WORKSPACE
    if not is_live:
        found_libs, cont = check_libraries_in_path(core_file, cnf.WORKSPACE)
        workspace = os.path.expanduser(cnf.WORKSPACE)
        core_file=os.path.expanduser(core_file)
        target_path = os.path.join(workspace, os.path.basename(core_file))
        #shutil.copy(core_file, target_path)

        src_abs = os.path.abspath(core_file)
        dst_abs = os.path.abspath(target_path)

        # Check if the source and destination are the same
        if src_abs == dst_abs:
            print("Source and destination are the same file. Skipping copy.")
        else:
            try:
                shutil.copy(core_file, target_path)
                print(f"Copied {core_file} to {target_path}")
            except Exception as e:
                print(f"An error occurred: {e}")
        if not cont:
            solib_path = ''
            sysroot = '/'
    file_name = "gdb_commands"
    directory = os.getcwd()
    file_path = os.path.join(directory, file_name)
    gdb_commands_absolute_path = os.path.abspath(file_path)
    
    remote_command = """
set environment IP_ADDRESS={}
set environment USERNAME={}
set environment PASSWORD={}
""".format(ip, user, pwd)
    gdb_commands = """
dir {}
file {}
set pagination off
set auto-solib-add on
set sysroot {}
set solib-search-path {}
info sharedlibrary
set architecture {}

python
import sys
import os
sys.executable = "{}"
sys.path.insert(0, "{}")
sys.path.append("{}")
sys.path.append("{}")
import end_command
from substitute_path import substitution
substitution("{}")
end
dir {}
""".format(cnf.WORKSPACE, binary_path, sysroot, solib_path, arch, python_path, site_package, 
           directory, gdb_commands_absolute_path, cnf.WORKSPACE, gdb_commands_absolute_path)
    if is_live and ui_mood=='gdb':
        gdb_commands += remote_command
        gdb_commands += """
target extended-remote {}:{}
attach {}
""".format(ip, port, pid)
    else:
        if ui_mood=='gdb':
            gdb_commands = """
            core-file {}
            """.format(core_file) + gdb_commands
    gdb_commands += "source __init__.py"
    return gdb_commands


def run_gdb_local(app, ip, port, pid, user, pwd,
                  arch="auto", is_live=True, core_file=None,ui_mood='gdb'):
    """Run gdb locally with specified parameters."""
    if arch is None:
        arch = "auto"
    print("here  eeee " , cnf.WORKSPACE  )
    binary_path = os.path.join(cnf.WORKSPACE, app)
    gdb_commands = create_gdbcommand(
        arch,
        user,
        pwd,
        ip,
        port,
        pid,
        is_live=is_live,
        core_file=core_file,
        ui_mood=ui_mood, 
        binary_path=binary_path)
    # Create a temporary file for the GDB commands
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.gdb') as tmp_file:
        tmp_file.write(gdb_commands)
        os.chmod(temp_file, 0o777)
        print( tmp_file.name)
    if ui_mood == 'gdb' : 
        try:
            gdb_command = (
                'gnome-terminal -- gdb-multiarch -x {} {}'
            ).format(tmp_file.name, binary_path)

            process = subprocess.Popen(gdb_command, shell=True)
            process.wait()
        except subprocess.SubprocessError as e:
            print("Error starting gdb: {}".format(e))

    if ui_mood == 'vscode' :
        if is_live :  
            generate_debug_config(
                mode= 'live' ,
                output_path="{}/.vscode/launch.json".format(cnf.WORKSPACE),
                ip=ip,
                port=port,
                binary_path=binary_path.strip('\n'),
                workspace=cnf.WORKSPACE.strip('\n'),
                gdb_script=tmp_file.name.strip('\n'),
                process_id=pid
            )
        else: 
            generate_debug_config(
                mode="coredump",
                output_path="{}/.vscode/launch.json".format(cnf.WORKSPACE),
                core_path=core_file.strip('\n'),
                binary_path=binary_path.strip('\n'),
                workspace=cnf.WORKSPACE.strip('\n'),
                gdb_script=tmp_file.name.strip('\n'),
            )


def get_program_name(user, ip, pwd, pid):
    """Get the program name from the gdbserver using SSH."""
    ssh_conn = SSHConnection(ip=ip, username=user, password=pwd)
    program = ''
    try:
        ssh_conn.connect()
        gdbserver_command = 'ps -p {} -o args='.format(pid)
        program, _ = ssh_conn.run_command(gdbserver_command)
        program = program.strip()
        if program.startswith('./'):
            program = program[2:]
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
