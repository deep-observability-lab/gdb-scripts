import gdb_commands.deadlock as deadlock
import gdb_commands.process as process
import gdb_commands.bins as bins
import gdb_commands.arena as arena
import gdb_commands.heap as heap
import gdb_commands.add_source_path as add_source_path
import gdb_commands.search_pattern as search_pattern
import gdb_commands.memsummary as memsummary
import importlib

importlib.reload(deadlock)
importlib.reload(process)
importlib.reload(bins)
importlib.reload(arena)
importlib.reload(heap)
importlib.reload(add_source_path)
importlib.reload(search_pattern)
importlib.reload(memsummary)

process.Process()
arena.Arena()
bins.Bins()
deadlock.DeadlockDetector()
heap.Heap()
add_source_path.AddChildDirectories()
search_pattern.SearchPatternCommand()
memsummary.MemSummary()