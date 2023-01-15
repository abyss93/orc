class Logger:

    def __init__(self, debug_enabled):
        self.debug_enabled = debug_enabled
        self.start_phrase = "DEBUG>>>"
        self.end_phrase = ">>>DEBUG"

    def log(self, debug_info, context=""):
        if self.debug_enabled:
            print(context + self.start_phrase)
            print(debug_info)
            print(self.end_phrase + context)
