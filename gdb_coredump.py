from gdb_automate import run_gdb_local, run_gdbserver, get_program_name
import argparse
from setup_local import setup_local
import config as cnf
import sys
import os 

YELLOW = '\033[93m'
RESET = '\033[0m'
def main(argv):
    parser = argparse.ArgumentParser(
        description='Take the path of coredump file and set the workspace for debugging coredump.')
    parser.add_argument(
    '-a', '--architecture', 
    type=str, 
    required=False,
    default='auto' ,  
    choices=[
        # x86 Family
        # 'i386', 'i386:x86-64', 'i386:x86-64:intel', 'i386:x86-64:32', 
        # 'i386:nacl', 'i386:x64-32:nacl',
        
        # ARM Family
        # 'aarch64', 'aarch64:ilp32',
        # 'arm', 'armv2', 'armv2a', 'armv3', 'armv3m', 'armv4', 'armv4t', 
        # 'armv5', 'armv5t', 'armv5te', 'xscale', 'ep9312', 'iwmmxt',
        # 'iwmmxt2', 'armv5tej', 'armv6', 'armv6k', 'armv6z', 'armv7', 
        # 'armv6-m', 'armv7-m', 'armv7e-m', 'armv8-a', 'armv8-r', 
        # 'armv8-m.base', 'armv8-m.main',

        # Alpha Family
        'alpha', 'alpha:ev4', 'alpha:ev5', 'alpha:ev6', 

        # Motorola 68k (m68k) Family
        # 'm68k:68000', 'm68k:68010', 'm68k:68020', 'm68k:68030', 
        # 'm68k:68040', 'm68k:68060', 'm68k:cpu32', 'm68k:fido', 
        # 'm68k:isa-a', 'm68k:isa-a:nodiv', 'm68k:isa-b', 'm68k:isa-c', 
        # 'm68k:isa-aplus', 'm68k:isa-a:mac', 'm68k:isa-a:nodiv:mac', 
        # 'm68k:isa-aplus:mac',

        # MIPS Family
        # 'mips', 'mips:3000', 'mips:3900', 'mips:4000', 'mips:4010', 
        # 'mips:4100', 'mips:4111', 'mips:4120', 'mips:4300', 'mips:4400',
        # 'mips:4600', 'mips:4650', 'mips:5900', 'mips:6000', 'mips:7000',
        # 'mips:8000', 'mips:9000', 'mips:10000', 'mips:12000', 'mips:14000',
        # 'mips:16000', 'mips:16', 'mips:5', 'mips:isa32', 'mips:isa32r5',
        # 'mips:isa32r6', 'mips:isa64', 'mips:isa64r2', 'mips:isa64r3', 
        # 'mips:isa64r5', 'mips:isa64r6', 'mips:loongson:2e', 'mips:loongson:2f',

        # PowerPC Family
        'auto' , 
        'powerpc:common', 'powerpc:403', 'powerpc:405', 'powerpc:601', 
        'powerpc:603', 'powerpc:604', 'powerpc:7400', 'powerpc:e300c3', 
        'powerpc:e300c4', 'powerpc:e500', 'powerpc:e500mc', 
        'powerpc:e500mc64', 'powerpc:e5500', 'powerpc:e6500', 
        'powerpc:titan', 'powerpc:vle',

        # RISC-V Family
        # 'riscv', 'riscv:rv32', 'riscv:rv64',

        # S390 Family
        # 's390', 's390:31-bit', 's390:64-bit',

        # SuperH (SH) Family
        # 'sh', 'sh2', 'sh2e', 'sh3', 'sh3-dsp', 'sh4', 'sh4a', 'sh4al-dsp', 
        # 'sh4al-dsp:fp', 'sh4-nommu', 'sh2a', 'sh2a-nommu',

        # SPARC Family
        # 'sparc', 'sparc:common', 'sparc:sparclite', 'sparc:sparclite_le',
        # 'sparc:v8', 'sparc:v8plus', 'sparc:v8plusv', 'sparc:v8plusv:le',
        # 'sparc:v9', 'sparc:v9a', 'sparc:v9b', 'sparc:v9d',

        # Miscellaneous Architectures
        # 'm32r', 'm32r:nommu', 'auto'
    ],
    help=(
        'Architecture for the cross-compiled binary. Use specific architecture '
        'variants as listed. Examples: powerpc:common, mips:isa32r5, sparc:v9.'
    ))
    parser.add_argument('-c', '--coredump', type=str, required=True,
                        help='name of coredump file which should be located on workspace path.')
    parser.add_argument('-p', '--program', type=str, required=True, 
                        help='name of the binary program you wish to debug.')
    parser.add_argument('-w', '--workspace', type=str,
                        default="/work" ,
                        help='Directory where you should put all the shared-binaries/app-binary and source codes.')
    parser.add_argument('-ui', '--user_interface', type=str,
                    choices=['vscode', 'gdb'],
                    default='gdb',
                    help='Specifies the user interface for debugging. Default: "gdb". Options: "vscode" for Visual Studio Code or "gdb" for GDB CLI.'
                    )
    
    args = parser.parse_args()
    environment = ''
    workspace = args.workspace
    
    ui_mood = 'vscode' if args.user_interface == 'vscode' else 'gdb'
   
    if workspace== None and os.path.exists('/.dockerenv') == False : 
        workspace = '/work'
        print("{}Warning: Default path for WORKSPACE '{}' will be used.{}".format(YELLOW, workspace, RESET))
    
    if os.path.exists('/.dockerenv') and args.user_interface == 'vscode':
        environment = workspace
        workspace = '/work'
    elif os.path.exists('/.dockerenv') and args.user_interface == 'gdb' : 
        environment = ''
        workspace = '/work'

    cnf.init(workspace=workspace, coredump=args.coredump , environment = environment)

    # setup = setup_local()
    # setup.setup_local()
    core_file_path = os.path.join( workspace,args.coredump ).strip()
    
    if (not os.path.exists(core_file_path) ) and ( not os.path.exists( os.path.join('/work' , args.coredump)) ) :
        print("{} does not exist at {}".format(args.coredump , args.workspace))
        exit()
    
    run_gdb_local(args.program, port=None, pid=None, user=None,
                  pwd=None, ip=None, arch=args.architecture, is_live=False, core_file=args.coredump, 
                  ui_mood=ui_mood)


if __name__ == "__main__":
    main(sys.argv[1:])
