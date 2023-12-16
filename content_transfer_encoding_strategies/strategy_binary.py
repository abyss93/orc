class StrategyBinary:
    CLASS_NAME = "StrategyBinary"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        # Unencoded 8-bit ASCII
        self.logger.log("Binary | Content-Type: " + str(content_type), StrategyBinary.CLASS_NAME)

        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(payload)

        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            # TODO
            self.utils.hashes_of(payload)
