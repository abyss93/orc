class Strategy8bit:
    CLASS_NAME = "Strategy8bit"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        # Unencoded 8-bit ASCII
        self.logger.log("Unencoded 8-bit ASCII | Content-Type: " + str(content_type), Strategy8bit.CLASS_NAME)

        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(payload)

        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            # TODO
            print("8bit")
