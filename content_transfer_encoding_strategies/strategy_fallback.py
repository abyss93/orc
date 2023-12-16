import quopri


class StrategyFallback:
    CLASS_NAME = "StrategyFallback"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        # Encoded 7-bit ASCII
        self.logger.log("Quoted Printable | Content-Type: " + str(content_type), StrategyFallback.CLASS_NAME)
        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(payload)

        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            if self.config["debug"]: self.logger.log(payload)
            self.utils.find_urls(payload)
            # TODO
