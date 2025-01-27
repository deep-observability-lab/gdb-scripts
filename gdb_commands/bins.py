import gdb
from gdb_commands.global_state import state_manager
from gdb_commands.pretty_print import PrettyPrinter

label_color = PrettyPrinter.LABEL_COLOR
reset_color = PrettyPrinter.RESET_COLOR


class Bins(gdb.Command):
    def __init__(self):
        super(Bins, self).__init__("bins", gdb.COMMAND_USER)

    # check the head of small / large / unsorted bins and follow the chunks.
    # get the chunk count.
    def get_head(self, indx, ar_add):
        if indx == 0:
            return 0
        bin_head = gdb.parse_and_eval(
            "( *(struct malloc_state*) {}).bins[{}]".format(ar_add, indx * 2 - 2))

        return bin_head

    def walk_doubled_link_bin_at(self, index, name, bin_head):
        if bin_head == 0:
            return
        head = str(bin_head).split()[0]
        cur = head
        bin_head = cur
        pre = cur
        num_chunks = 0
        while True:
            mchunkptr = gdb.parse_and_eval("*(mchunkptr) {}".format(cur))
            fd = str(mchunkptr['fd']).split()[0]
            bk = str(mchunkptr['bk']).split()[0]
            if num_chunks == 0:
                pre = bk

            if fd == bin_head:
                break
            if bk != pre:
                PrettyPrinter.print_error(
                    "corruption at {} bin with index: {} with head ptr: {} at chunk {}\nprevious chunck is {}".format(
                        name, index, head, cur, pre))
                return
            num_chunks += 1
            pre = cur
            cur = fd

        if num_chunks != 0:
            PrettyPrinter.print_row(
                "{}{}[{}] at {} {}".format(
                    label_color,
                    name,
                    index,
                    str(bin_head).split()[0],
                    reset_color),
                "{} chunks".format(num_chunks),
                width=100)

    def walk_unsorted_bin(self, ar_add):
        PrettyPrinter.print_devider(100)
        PrettyPrinter.print_half_header("Unsorted bins")
        bin_head = self.get_head(1, ar_add)
        self.walk_doubled_link_bin_at(1, 'Unosrtedbins', bin_head)

    def walk_fast_bin(self, ar_add):
        PrettyPrinter.print_devider(100)
        PrettyPrinter.print_half_header("fast bins")

        for i in range(10):
            fbin_head = gdb.parse_and_eval(
                "( *(struct malloc_state*) {}).fastbinsY[{}]".format(ar_add, i))
            if fbin_head == 0:
                PrettyPrinter.print_row(
                    "{}Fastbin[{}] {}".format(label_color, i, reset_color),
                    "0 chunks",
                    width=100
                )
                continue
            cur = str(fbin_head).split()[0]
            num_chunks = 0
            while cur != "0x0":  # Continue until fd points to NULL
                try:
                    mchunkptr = gdb.parse_and_eval(
                        "*(mchunkptr) {}".format(cur))

                    fd = str(mchunkptr['fd']).split()[0]
                    num_chunks += 1
                    cur = fd

                except gdb.MemoryError:
                    PrettyPrinter.print_error(
                        "Cannot access memory at address {}, stopping.".format(cur))
                    break

            if num_chunks != 0:
                PrettyPrinter.print_row(
                    "{}Fastbin[{}] at {} {}".format(
                        label_color,
                        i,
                        str(fbin_head).split()[0],
                        reset_color),
                    "{} chunks".format(num_chunks),
                    width=100)

    def walk_small_bins(self, ar_add):
        PrettyPrinter.print_devider(100)
        PrettyPrinter.print_half_header("Small bins")

        for i in range(2, 64):
            bin_head = self.get_head(i, ar_add)
            self.walk_doubled_link_bin_at(i, 'Smallbins', bin_head)

    def walk_large_bins(self, ar_add):
        PrettyPrinter.print_devider(100)
        PrettyPrinter.print_half_header("Large bins")
        for i in range(64, 127):
            bin_head = self.get_head(i, ar_add)
            self.walk_doubled_link_bin_at(i, 'Largebins', bin_head)

    def invoke(self, arg, from_tty):
        table_width = 100
        state_manager.bins = []
        PrettyPrinter.print_header("Analysing Bins", width=table_width)
        for ar in state_manager.arenas:
            PrettyPrinter.print_half_header(
                "Bins for arena at {}".format(ar),
                color=PrettyPrinter.RED_COLOR
            )
            if len(state_manager.arena2heaps[ar]) > 0:
                self.walk_fast_bin(ar)
                self.walk_unsorted_bin(ar)
                self.walk_small_bins(ar)
                self.walk_large_bins(ar)
        PrettyPrinter.print_footer()
