import quopri


class StrategyQuotedPrintable:
    CLASS_NAME = "StrategyQuotedPrintable"

    def __init__(self, config, logger, utils):
        self.logger = logger
        self.utils = utils
        self.config = config

    def process(self, content_type, payload):
        # Encoded 7-bit ASCII
        self.logger.log("Quoted Printable | Content-Type: " + str(content_type), StrategyQuotedPrintable.CLASS_NAME)
        # join preserving \n because while it is useful not to have \n in base64, newlines are needed
        # to correctly process the body in quoted-printable elements (e.g. HTML code) https://www.rfc-editor.org/rfc/rfc2045#section-6.7
        body = ''.join(payload)
        decoded = quopri.decodestring(body).decode("utf-8")
        if self.config["print_payload"]:
            print("**RAW PAYLOAD**")
            print(decoded)

        if self.config["payload_analysis"]:
            print("**PAYLOAD ANALYSIS**")
            if self.config["debug"]: self.logger.log(body)
            self.utils.find_urls(decoded)
            # TODO
