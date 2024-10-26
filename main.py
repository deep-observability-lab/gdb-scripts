from gdb_automate import run_gdb_local , run_gdbserver
import argparse
from installations import installation

def main(argv):
    parser = argparse.ArgumentParser(description='connect to gdbserver on remote and\nattach one process on special port.')
    parser.add_argument('-ip' , '--ip' ,type=str , required=True , help='ip address of remote board (e.g. 192.168.5.5)' )
    parser.add_argument('-u' , '--username' , type=str , required=True , help='username on the remote board (e.g. root)')
    parser.add_argument('-pid', '--process_id', type=str, required=True, help='Process ID (e.g. 1234)')
    parser.add_argument('-password' , '--password' ,type=str , required=True , help='password for authentication on remote board.' )
    parser.add_argument("-app" , "--application" , type=str , required=True , help="name of binary debugging process is belong.")
    parser.add_argument("-arch" , "--architecture" , type=str , required=False , help="architecture set for cross-compiled binary, powerpc:common is the default architecture.")
    args = parser.parse_args()
    installation()
    port = run_gdbserver(user=args.username , pwd=args.password , ip= args.ip)
    run_gdb_local(app=args.application, port = port , pid=args.process_id , rel=args.release, user=args.username , pwd=args.password, ip= args.ip , arch = args.architecture )

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])