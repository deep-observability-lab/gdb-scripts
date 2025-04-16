import gdb
from gdb_commands.pretty_print import PrettyPrinter

label_color = PrettyPrinter.LABEL_COLOR
reset_color = PrettyPrinter.RESET_COLOR


class ThreadInfo:
    def __init__(self):
        self.frames = []
        self.waiting_for_thread = None
        self.thread_id = None

    def __str__(self):
        return "Thread ID: {}, Waiting for: {}".format(
            self.thread_id, self.waiting_for_thread)


class DeadlockDetector(gdb.Command):
    """Detects potential deadlocks among threads in the current process."""

    def __init__(self):
        super().__init__("deadlock", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        PrettyPrinter.print_header("deadlock detection analysis", width=100)
        thread_map = self.collect_thread_info()
        self.analyze_threads(thread_map)
        PrettyPrinter.print_footer()

    def collect_thread_info(self):
        """Collects information about all threads in the current process."""
        thread_map = {}
        for process in gdb.inferiors():
            PrettyPrinter.print_half_header(
                "Analyzing Process ID: {}".format(process.pid),
                color=PrettyPrinter.BLUE_COLOR)

            for thread in process.threads():
                thread_info = ThreadInfo()
                thread_info.thread_id = thread.ptid[1]
                thread.switch()
                current_frame = gdb.selected_frame()

                PrettyPrinter.print_half_header(
                    "Inspecting Thread ID: {}".format(thread_info.thread_id),
                    color=PrettyPrinter.LABEL_COLOR)
                while current_frame:
                    current_frame.select()
                    frame_name = current_frame.name() or "Unknown"
                    if "pthread_mutex_lock" in frame_name:
                        try:
                            owner = int(
                                gdb.execute(
                                    "print mutex.__data.__owner",
                                    to_string=True).split()[2])
                            thread_info.waiting_for_thread = owner
                            PrettyPrinter.print_half_header(
                                "Thread {} waiting on mutex owned by {}".format(
                                    thread_info.thread_id, owner),
                                color=PrettyPrinter.ORANGE_COLOR)
                        except Exception as e:
                            PrettyPrinter.print_half_header(
                                "Error retrieving mutex owner: {}".format(
                                    str(e)),
                                color=PrettyPrinter.RED_COLOR)
                    thread_info.frames.append(frame_name)
                    current_frame = current_frame.older()

                thread_map[thread_info.thread_id] = thread_info
        return thread_map

    def analyze_threads(self, thread_map):
        """Analyzes collected thread information to detect deadlocks."""
        deadlocked_pairs = []

        for tid, thread in thread_map.items():
            if thread.waiting_for_thread:
                waiting_tid = thread.waiting_for_thread
                if waiting_tid in thread_map and thread_map[waiting_tid].waiting_for_thread == tid:
                    deadlocked_pairs.append((tid, waiting_tid))
                    status = "DEADLOCKED"
                    PrettyPrinter.print_half_header(
                        "Deadlock detected: Thread {} <-> Thread {}".format(
                            tid, waiting_tid),
                        color=PrettyPrinter.RED_COLOR)
                else:
                    status = "Waiting"
                    PrettyPrinter.print_half_header(
                        "Thread {} is waiting for Thread {} - Status: {}".format(
                            tid, waiting_tid, status), color=PrettyPrinter.YELLOW_COLOR)

        if deadlocked_pairs:
            PrettyPrinter.print_header(
                "Summary of Detected Deadlocks", width=60)
            for t1, t2 in deadlocked_pairs:
                PrettyPrinter.print_half_header(
                    "Deadlocked Pair: Thread {} and Thread {}".format(t1, t2),
                    color=PrettyPrinter.PURPLE_COLOR)
        else:
            PrettyPrinter.print_header(
                "No deadlocks detected.",
                width=60)
                # color=PrettyPrinter.LABEL_COLOR
