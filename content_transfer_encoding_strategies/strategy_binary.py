class StrategyBinary:
    def __init__(self, logger, hash_service):
        self.logger = logger
        self.hash_service = hash_service

    def process(self, to_process):
        # Unencoded 8-bit ASCII
        # TODO
        print("8bit")
        self.hash_service.hashes_of(to_process)
