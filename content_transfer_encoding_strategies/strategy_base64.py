import base64


class StrategyBase64:
    CLASS_NAME = "StrategyBase64"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        self.logger.log("BASE64 | Content-Type: " + str(content_type), StrategyBase64.CLASS_NAME)

        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(payload)
            
        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            body = ''.join(payload).replace("\n", "")
            decoded = base64.b64decode(body)
            if self.config["debug"]: self.logger.log(body)
            self.utils.hashes_of(decoded)
            # print(decoded)
            # if self.config["find_urls"]: self.utils.find_urls(decoded)
            # TODO
