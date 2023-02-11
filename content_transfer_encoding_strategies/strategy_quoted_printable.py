import quopri


class StrategyQuotedPrintable:
    def __init__(self, config, logger, utils):
        self.config = config
        self.logger = logger
        self.utils = utils

    def process(self, content_type, to_process, p_body_start):
        # Encoded 7-bit ASCII
        # join preserving \n because while it is useful not to have \n in base64, newlines are needed
        # to correctly process the body in quoted-printable elements (e.g. HTML code) https://www.rfc-editor.org/rfc/rfc2045#section-6.7
        body = ''.join(to_process[p_body_start:])
        decoded = quopri.decodestring(body).decode("utf-8")
        if self.config["debug"]: self.logger.log(body)
        print(decoded) # fa rumore, forse posso togliere il print e fixare i test
        if self.config["find_urls"]: self.utils.find_urls(decoded)
        # TODO
