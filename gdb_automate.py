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
    ssh_conn.close()
    return 0

def find_directories_with_lib(workspace):
    """Search for all directories containing 'lib' in their names within the workspace path."""
    matching_directories = []
    for root, dirs, _ in os.walk(workspace):
        for dir_name in dirs:
            if 'lib' in dir_name:  
                matching_directories.append(os.path.join(root, dir_name))
    return matching_directories

def extract_shared_libraries_from_core_file(core_dump_path, binary_path):
    """Extract shared libraries using gdb."""
    try:
        gdb_cmd = f"gdb-multiarch {binary_path} {core_dump_path} --batch -ex 'info sharedlibrary'"
        result = subprocess.run(
            gdb_cmd, shell=True, capture_output=True, text=True, check=True
        )
        so_paths = []
        for line in result.stdout.splitlines():
            match = re.search(r"(/.+\.so(?:\.[\d]+)*)", line)
            if match:
                lib = match.group(1)
                so_paths.append(lib)
        return so_paths
    except subprocess.CalledProcessError as e:
        print("Error running gdb: {}".format(e))
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return []

def find_libraries_in_workspace(workspace, library_name):
    """Search for files containing library_name in the workspace directory."""
    found_files = []
    for root, _, files in os.walk(workspace):
        for file in files:
            if (library_name in file) or (file in library_name ):
                found_files.append(os.path.join(root, file))

    return found_files if found_files else None

def check_libraries_in_path(core_dump_path, search_path, binary_path):
    """Checks how many shared libraries exist in the given path."""
    found = set()
    not_found = set()
    libraries = extract_shared_libraries_from_core_file(
        os.path.join(cnf.WORKSPACE, core_dump_path) , binary_path)
    for lib in libraries:
        found_path = find_libraries_in_workspace(search_path, os.path.basename(lib))
        if found_path is not None:
            for l in found_path:
                found.add(os.path.dirname(l))
        else:
            not_found.add(lib)
    tmp_lib = find_directories_with_lib(cnf.WORKSPACE)
    for l in tmp_lib : 
        found.add( l )
  
    result = True
    if len(not_found) > 0:
        print("Following libraries were not found in workspace.")
        for lib in not_found:
            print("  - {}".format(os.path.basename(lib)))
        cont = input(
            "[1] Continue with whatever libraries found in workspace.\n"
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
            parent_dirs = [os.path.dirname(lib) for lib in not_found]
            found = list( found ) + parent_dirs
            print( found )
            cont=False 
        else:
            print("Invalid input. Exiting the program.")
            exit(1)  # Exit with error code
    return found, result


def is_stripped(binary_path):
    """Check if the binary is stripped or not."""
    if not os.path.isfile(binary_path):
        print("Error: The path '{}' is not a valid file.".format(binary_path))
        return None
    try:
        # Run the readelf command to check for symbols
        command = "file {}".format(binary_path)
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT).decode()
        # If the output contains symbol table entries, the binary is not
        # stripped
        if "not stripped" in output:
            return False  # Not stripped
        elif "stripped" in output:
            return True
        else:
            return False  # Stripped
    except subprocess.CalledProcessError as e:
        print("Error while executing file: {}".format(e.output.decode()))
        exit()

def extract_shared_libs(ip, username, password, pid, is_live, core_path):
    libs_path = ''
    try:
        result = None
        list_libs = None
        ssh = SSHConnection(ip=ip, username=username, password=password)
        ssh.connect()
        command = "cat /proc/{}/maps | grep '\\.so' | sed 's,.*/\\(.*.so\\),\\1,' | sort -u".format(
            pid)
        if username != "root":
            command = 'echo "{}" | sudo -S cat /proc/{}/maps | grep "\\.so" | sed "s,.*/\\(.*.so\\),\\1," | sort -u'.format(
                password, pid)
        output, _ = ssh.run_command(command)
        result = output.strip()
        list_libs = result.split()
            
        non_stripped = {}
        
        if list_libs:
            for i in range(len(list_libs)):   
                find_command = "find {} -type f -name '{}'".format(
                    cnf.WORKSPACE, list_libs[i])
                paths = subprocess.check_output(
                    find_command, shell=True).decode().strip()
                first_path = ""
                if paths:
                    splited_pathes = paths.split()
                    
                    first_path = splited_pathes[0]
                    for p in splited_pathes:
                        if is_stripped(p) == False:
                            token = p.split('/')
                            lib_name = token[len(token) - 1]
                            non_stripped[lib_name] = p
                            libs_path += p.replace(list_libs[i], '')
                            if i != len(list_libs) - 1:
                                libs_path += ':'
                            first_path="0"
                            break
                    if first_path != "0" : 
                        token = first_path.split('/')
                        lib_name = token[len(token) - 1]
                        non_stripped[lib_name] = first_path
                        libs_path += p.replace(list_libs[i], '')
                        if i != len(list_libs) - 1:
                            libs_path += ':'
        else:
            print("No shared libraries found.")
        
    except Exception as e:
        print("Error: {}".format(e))
        exit()
    finally:
        if is_live: 
            ssh.close()
        return non_stripped


def create_gdbcommand(arch, user, pwd, ip, port, pid, binary_path,
                      is_live=True, core_file=None, ui_mood='gdb'):
    python_path = sys.executable
    site_package = site.getsitepackages()[0]
    solib_path = cnf.WORKSPACE
    sublibs = ""
    if is_live : 
        sublibs = extract_shared_libs(ip, user, pwd, pid, is_live, core_file)
    sysroot = cnf.WORKSPACE
    cont = False
    found_libs = set()
    tmp_lib = find_directories_with_lib(cnf.WORKSPACE)

    if not is_live:
        found_libs, cont = check_libraries_in_path(core_file, cnf.WORKSPACE, binary_path)
        workspace = os.path.expanduser(cnf.WORKSPACE)
        core_file = os.path.expanduser(core_file)
        target_path = os.path.join(workspace, os.path.basename(core_file))
        if len(found_libs) > 0:
            solib_path = ':'.join(found_libs)
        if not cont:
            sysroot = '/'

    file_name = "gdb_commands/"
    directory = os.getcwd()
    file_path = os.path.join(directory, file_name)
    gdb_commands_absolute_path = os.path.abspath(file_path)
    gdb_commands=''
    remote_command = """
set environment IP_ADDRESS={}
set environment USERNAME={}
set environment PASSWORD={}
""".format(ip, user, pwd)
    if is_live and ui_mood == 'gdb':
        gdb_commands += remote_command
        
    gdb_commands += """
set python print-stack full
dir {}
file {}
set pagination off
set auto-solib-add on
# set sysroot {}
set sysroot .
core-file $core-file
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
sys.path.append("{}")
from end_command import ExitCommand
ExitCommand()
# substitution("{}")
end
dir {}
""".format(
        cnf.WORKSPACE,
        binary_path,
        sysroot,
        solib_path,
        # sublibs,
        arch,
        python_path,
        site_package,
        directory,
        site_package,
        gdb_commands_absolute_path,
        cnf.WORKSPACE,
        gdb_commands_absolute_path)
    if not cont and (is_live ==False) :
        gdb_commands = gdb_commands.replace('set sysroot .', 'set sysroot /')

    if is_live and ui_mood == 'gdb':
        gdb_commands += """
target extended-remote {}:{}
attach {}
""".format(ip, port, pid)
        gdb_commands = gdb_commands.replace("$core-file", '')
        gdb_commands = gdb_commands.replace("core-file", '')
    else:
        if ui_mood == 'gdb':
            gdb_commands = gdb_commands.replace("$core-file", core_file)
        else:
            gdb_commands = gdb_commands.replace("$core-file", '')
            gdb_commands = gdb_commands.replace("core-file", '')
    
    gdb_commands += "source __init__.py\n"
    if is_live and len( sublibs ) > 0 : 
        sublibs
        gdb_commands += """
python
from gdb_commands.find_libs import GetSharedLibraries
GetSharedLibraries()  
end
get_shared_libs {}
""".format( sublibs)  
    if cnf.SRC_ENV != '' and cnf.SRC_ENV is not None:
        gdb_commands += "add_child_dirs {}\n".format(cnf.SRC_ENV)
    if cnf.ENV != '': 
        gdb_commands = gdb_commands.replace(cnf.WORKSPACE, cnf.ENV)
        host_path = os.environ.get("HOST_PATH")
        if host_path:
            gdb_commands = gdb_commands.replace('/app', host_path)
    return gdb_commands


def run_gdb_local(app, ip, port, pid, user, pwd, source=None,
                  arch="auto", is_live=True, core_file=None, ui_mood='gdb'):
    """Run gdb locally with specified parameters."""
    if arch is None:
        arch = "auto"

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
        os.chmod(str(tmp_file.name), 0o777)
        tmp_file.close()
        shutil.copy(tmp_file.name, cnf.WORKSPACE)
    gdb_script_path = str(tmp_file.name).split('/')[-1]

    if ui_mood == 'gdb':
        try:
            gdb_command = (
                'tmux new-session "cd {} && gdb-multiarch -x {} {}"'
            ).format(cnf.WORKSPACE, gdb_script_path, binary_path)
            process = subprocess.Popen(gdb_command, shell=True)
            process.wait()
        except subprocess.SubprocessError as e:
            print("Error starting gdb: {}".format(e))

    if ui_mood == 'vscode':
        binary_relative_path = ''
        try:
            binary_relative_path = (
                binary_path.strip('\n')).split(
                cnf.WORKSPACE.strip('\n'))[1]
        except BaseException:
            print("there is problem with path of binary file ")
            exit()
        if is_live:
            generate_debug_config(
                mode='live',
                output_path="{}/.vscode/launch.json".format(cnf.WORKSPACE),
                ip=ip,
                port=port,
                binary_path='/' + binary_relative_path,
                workspace=cnf.WORKSPACE.strip('\n'),
                gdb_script=gdb_script_path,
                process_id=pid,
                live=is_live
            )
        else:
            generate_debug_config(
                mode="coredump",
                output_path="{}/.vscode/launch.json".format(cnf.WORKSPACE),
                core_path=core_file.strip('\n'),
                binary_path='/' + binary_relative_path,
                workspace=cnf.WORKSPACE.strip('\n'),
                gdb_script=gdb_script_path,
                live=is_live
            )


def get_program_name(user, ip, pwd, pid):
    """Get the program name from the gdbserver using SSH."""
    ssh_conn = SSHConnection(ip=ip, username=user, password=pwd)
    program = ''
    try:
        ssh_conn.connect()
        gdbserver_command = 'ps -p {} -o args='.format(pid)
        program, _ = ssh_conn.run_command(gdbserver_command)
        program = program.strip().split('/')[-1]
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