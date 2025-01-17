from end_command import ExitCommand
from deadlock import DeadlockDetector
from process import Process
from bins import Bins
from arena import Arena
from heap import Heap
import gdb
import importlib
import sys
import os
from pretty_print import PrettyPrinter


gdb.execute('info sharedlibrary')
output = gdb.execute('info sharedlibrary', to_string=True)

output = gdb.execute('info sharedlibrary', to_string=True)

lines = output.splitlines()
# for line in lines:
#     if 'libc.so.6' in line:
#         # Check if the row contains 'Yes (*)', meaning it is loaded with debug symbols
#         if 'Yes (*)' in line:            
#             current_dir = os.path.dirname(os.path.abspath(__file__))
#             if current_dir not in sys.path:
#                 sys.path.insert(0, current_dir)

#             # Reload modules if already imported
#             module_names = list(sys.modules.keys())
#             for module_name in module_names:
#                 if module_name in ['heap', 'arena', 'bins', 'process' , 'DeadlockDetector']:
#                     importlib.reload(sys.modules[module_name])
#             Process()
#             Arena()
#             Bins()
#             DeadlockDetector()
#             Heap()
#         else:
#             PrettyPrinter.print_error("libc.so.6 is loaded, but without debug symbols. command for memory debuging is not accessible.")
#             # return None
#             DeadlockDetector()
#             ExitCommand()
    
Process()
Arena()
Bins()
DeadlockDetector()
Heap()
ExitCommand()
