from gdb_commands.deadlock import DeadlockDetector
from gdb_commands.process import Process
from gdb_commands.bins import Bins
from gdb_commands.arena import Arena
from gdb_commands.heap import Heap
from gdb_commands.add_source_path import AddChildDirectories
from gdb_commands.search_pattern import SearchPatternCommand
from gdb_commands.memsummary import MemSummary
import gdb

gdb.execute('info sharedlibrary')
output = gdb.execute('info sharedlibrary', to_string=True)

output = gdb.execute('info sharedlibrary', to_string=True)

lines = output.splitlines()

Process()
Arena()
Bins()
DeadlockDetector()
Heap()
AddChildDirectories()
SearchPatternCommand()
MemSummary()
