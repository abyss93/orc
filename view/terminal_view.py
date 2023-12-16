import random

class TerminalView:
    STYLES = {
        # "black": "\033[30m",
        # "red": "\033[31m",
        # "green": "\033[32m",
        # "yellow": "\033[33m",
        # "blue": "\033[34m",
        # "magenta": "\033[35m",
        # "cyan": "\033[36m",
        # "lightgray": "\033[37m",
        # "darkgray": "\033[90m",
        # "lightred": "\033[91m",
        # "lightgreen": "\033[92m",
        # "lightyellow": "\033[93m",
        # "lightblue": "\033[94m",
        # "lightmagenta": "\033[95m",
        # "lightcyan": "\033[96m",
        # "white": "\033[97m",
        # "backgrounddefault": "\033[49m",
        # "backgroundblack": "\033[40m",
        "backgroundred": "\033[41m",
        "backgroundgreen": "\033[42m",
        "backgroundyellow": "\033[43m",
        "backgroundblue": "\033[44m",
        "backgroundmagenta": "\033[45m",
        "backgroundcyan": "\033[46m",
        # "backgroundlightgray": "\033[47m",
        # "backgrounddarkgray": "\033[100m",
        "backgroundlightred": "\033[101m",
        "backgroundlightgreen": "\033[102m",
        "backgroundlightyellow": "\033[103m",
        "backgroundlightblue": "\033[104m",
        "backgroundlightmagenta": "\033[105m",
        "backgroundlightcyan": "\033[106m",
        # "backgroundwhite": "\033[107m"
    }

    STYLES_ADHOC = {
        "end": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "underlined": "\033[4m",
        "blink": "\033[5m",
        "reverse": "\033[7m",
        "hidden": "\033[8m",
        "resetbold": "\033[21m",
        "resetdim": "\033[22m",
        "resetunderlined": "\033[24m",
        "resetblink": "\033[25m",
        "resetreverse": "\033[27m",
        "resethidden": "\033[28m",
        "default": "\033[39m",
    }

    def __init__(self, print_color):
        self.print_color = print_color

    # https://www.rfc-editor.org/rfc/rfc5321.html#section-4.4
    # https://www.rfc-editor.org/rfc/rfc7489#section-3.1.1
    # https://stackoverflow.com/questions/21480430/can-a-message-have-multiple-senders
    def print_headers(self, headers):
        for k, v in headers:
            color = random.choice(list(self.STYLES.keys()))
            self.internal_printc(color, f"{k}: {v}")

    def print_parsed_payloads(self, payloads):
        for i, p in enumerate(payloads):
            color = random.choice(list(self.STYLES.keys()))
            self.internal_printc(color, "__PAYLOAD__" + str(i))
            print(p)
            self.internal_printc(color, "__END_PAY__" + str(i))

    def print_text_plain(self, whole_content):
        print("____TEXT_PLAIN____")
        whole_content_lines = whole_content.splitlines(True)
        text_plain_index = whole_content_lines.index("\n") + 1  # end of headers section, plus 1 to exclude the \n line
        text_plain = "".join(whole_content_lines[text_plain_index:])
        print(text_plain)
        print("__END_TEXT_PLAIN__")

    def internal_printc(self, color, text, end="newline"):
        if self.print_color:
            if end == "":
                print(self.STYLES[color] + text + self.STYLES_ADHOC["end"], end="")
            else:
                print(self.STYLES[color] + text + self.STYLES_ADHOC["end"])
        else:
            if end == "":
                print(text, end="")
            else:
                print(text)