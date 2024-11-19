# pretty_print.py


class PrettyPrinter:
    HEADER_COLOR = "\033[1;33m"  # Yellow
    BORDER_COLOR = "\033[1;34m"  # Blue
    LABEL_COLOR = "\033[1;32m"   # Green
    ORANGE_COLOR = "\033[38;5;214m"  # Orange
    RESET_COLOR = "\033[0m"      # Reset
    RED_COLOR = "\033[1;31m"     # Red
    YELLOW_COLOR = "\033[0;33m"  # Yellow (Normal)
    PURPLE_COLOR = "\033[1;35m"  # Purple (Bold)
    @staticmethod
    def print_header(title, width=70):
        print(PrettyPrinter.BORDER_COLOR + "=" *
              width + PrettyPrinter.RESET_COLOR)
        print(
            PrettyPrinter.HEADER_COLOR +
            title.center(width) +
            PrettyPrinter.RESET_COLOR)
        print(PrettyPrinter.BORDER_COLOR + "=" *
              width + PrettyPrinter.RESET_COLOR)


    @staticmethod
    def print_row(label, data, width=70):
        label_str = str(label).ljust(width // 2 - 2)
        data_str = str(data).ljust(width // 2 - 2)
        formatted_label = PrettyPrinter.LABEL_COLOR + \
            label_str + PrettyPrinter.RESET_COLOR
        print(f"| {formatted_label} | {data_str} |")

    @staticmethod
    def print_footer(width=70):
        print(PrettyPrinter.BORDER_COLOR + "=" *
              width + PrettyPrinter.RESET_COLOR)

    @staticmethod
    def print_devider(width=70):
        print(PrettyPrinter.HEADER_COLOR + "-" *
              width + PrettyPrinter.RESET_COLOR)

    @staticmethod
    def print_error(error):
        print(PrettyPrinter.RED_COLOR, error, PrettyPrinter.RESET_COLOR)

    @staticmethod
    def print_half_header(line, color="\033[38;5;214m"):
        print(color, line, PrettyPrinter.RESET_COLOR)


    @staticmethod
    def print_centered(text, width=70):
        print(text.center(width))