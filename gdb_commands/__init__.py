from process import Process
from bins import Bins
from arena import Arena
from heap import Heap
import gdb
import importlib
import sys
import os

# Add the directory of the current script to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Reload modules if already imported
module_names = list(sys.modules.keys())
for module_name in module_names:
    if module_name in ['heap', 'arena', 'bins', 'process']:
        importlib.reload(sys.modules[module_name])

# Import classes from your modules

# Initialize your classes
Heap()
Arena()
Bins()
Process()
