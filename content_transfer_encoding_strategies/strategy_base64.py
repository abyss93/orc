import base64


class StrategyBase64:
    def __init__(self, config, logger, utils):
        self.config = config
        self.logger = logger
        self.utils = utils

    def process(self, to_process, p_body_start):
        # Encoded 7-bit ASCII
        body = ''.join(to_process[p_body_start:]).replace("\n", "")
        decoded = base64.b64decode(body)
        if self.config["debug"]: self.logger.log(body)
        self.utils.hashes_of(decoded)
        # print(decoded)
        # if self.config["find_urls"]: self.utils.find_urls(decoded)
        # TODO
