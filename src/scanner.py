class Scanner:
    def __init__(self, source, error_reporter):
        self.source = source
        self.error_reporter = error_reporter

    def scan_tokens(self):
        self.error_reporter.error(1, 1, "Scanner Not Implemented")
        return []