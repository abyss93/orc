class Strategy7bit:
    CLASS_NAME = "Strategy7bit"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        self.logger.log("Unencoded 7-bit ASCII | Content-Type: " + str(content_type), Strategy7bit.CLASS_NAME)

        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(payload)

        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            res = []
            body = ''.join(payload)
            print(body)
            if "text/plain" in content_type:
                self.utils.find_urls(body)
            elif "text/html" in content_type:
                return self.utils.find_urls_html(body)
            return res
