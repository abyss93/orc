class Strategy7bit:
    CLASS_NAME = "Strategy7bit"

    def __init__(self, logger, utils):
        self.logger = logger
        self.utils = utils

    def process(self, content_type, to_process, p_body_start):
        self.logger.log("Unencoded 7-bit ASCII | Content-Type: " + str(content_type), Strategy7bit.CLASS_NAME)
        res = []
        if "text/plain" in content_type:
            res = self.__text_plain(to_process, p_body_start)
        elif "text/html" in content_type:
            res = self.__text_html(to_process, p_body_start)
        return res

    def __text_plain(self, to_process, p_body_start):
        body = ''.join(to_process[p_body_start:])
        print(body)
        self.utils.find_urls(body)

    def __text_html(self, to_process, p_body_start):
        body = ''.join(to_process[p_body_start:])
        print(body)
        return self.utils.find_urls_html(body)