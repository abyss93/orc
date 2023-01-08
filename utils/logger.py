class Logger:

    def __init__(self, debug_enabled):
        self.debug_enabled = debug_enabled
        self.start_phrase = "DEBUG>>>"
        self.end_phrase = ">>>DEBUG"

    def log(self, debug):
        if self.debug_enabled:
            print(self.start_phrase)
            print(debug)
            print(self.end_phrase)
