# pretty_print.py

class PrettyPrinter:
    HEADER_COLOR = "\033[1;33m"  # Yellow
    BORDER_COLOR = "\033[1;34m"  # Blue
    LABEL_COLOR = "\033[1;32m"   # Green
    RESET_COLOR = "\033[0m"      # Reset

    @staticmethod
    def print_header(title, width=70):
        print(PrettyPrinter.BORDER_COLOR + "=" * width + PrettyPrinter.RESET_COLOR)
        print(PrettyPrinter.HEADER_COLOR + title.center(width) + PrettyPrinter.RESET_COLOR)
        print(PrettyPrinter.BORDER_COLOR + "=" * width + PrettyPrinter.RESET_COLOR)

    @staticmethod
    def print_row(label, data, width=70):
        label_str = str(label).ljust(width // 2 - 2)
        data_str = str(data).ljust(width // 2 - 2)
        formatted_label = PrettyPrinter.LABEL_COLOR + label_str + PrettyPrinter.RESET_COLOR
        print(f"| {formatted_label} | {data_str} |")

    @staticmethod
    def print_footer(width=70):
        print(PrettyPrinter.BORDER_COLOR + "=" * width + PrettyPrinter.RESET_COLOR)

    @staticmethod
    def print_line(line):
        print(line)

    @staticmethod
    def print_centered(text, width=70):
        print(text.center(width))
