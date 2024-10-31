from gdb_automate import run_gdb_local, run_gdbserver, get_program_name
import argparse
from setup_local import setup_local
import config as cnf
import sys
# ANSI escape codes for colored text
YELLOW = '\033[93m'
RESET = '\033[0m'


def main(argv):
    import getpass
    parser = argparse.ArgumentParser(
        description='Connect to a remote gdbserver and attach to a process running on a specified port.')
    parser.add_argument('-i', '--ip', type=str, required=True,
                        help='IP address of the remote target (e.g., 192.168.5.5).')
    parser.add_argument('-u', '--username', type=str, required=True,
                        help='Username for authentication on the remote target (e.g., root).')
    parser.add_argument('-pid', '--process_id', type=str, required=True,
                        help='Process ID of the target process (e.g., 1234).')
    parser.add_argument('-a', '--architecture', type=str,
                        help='Architecture for the cross-compiled binary. Defaults to "auto" if not specified.')
    parser.add_argument('-w', '--workspcae', type=str,
                        help='Directory where you should put all the shared-binaries/app-binary and source codes.')
    parser.add_argument('-p', '--port', type=int,
                        help='Port to set the DEFAULT_PORT. If not specified, gdb use port: 1234.')

    args = parser.parse_args()
    workspace = None
    gdb_port = None
    password = None
    if args.workspcae != None:
        workspace = args.workspcae
    else:
        print("{}Warning: Default path for WORKSPACE '/var/sysroot/' will be used.{}".format(YELLOW, RESET))

    if password == None:
        password = getpass.getpass(prompt="Enter password for remtoe target :")

    if args.port is not None:
        gdb_port = args.port

    cnf.init(workspace=workspace, default_port=gdb_port)

    setup = setup_local(ip=args.ip, user=args.username, pwd=password)

    setup.setup_local()

    port = run_gdbserver(user=args.username, pwd=password, ip=args.ip)

    p_name = get_program_name(
        user=args.username, ip=args.ip, pwd=password, pid=args.process_id)

    run_gdb_local(p_name, port=port, pid=args.process_id, user=args.username,
                  pwd=password, ip=args.ip, arch=args.architecture)


if __name__ == "__main__":
    main(sys.argv[1:])
