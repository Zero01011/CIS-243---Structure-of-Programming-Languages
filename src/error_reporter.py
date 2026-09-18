import sys

class ErrorReporter:
    """Class for reporting file mode and repl mode errors."""

    def __init__(self):
        self.had_error = False

    def error(self, line, column, error_message):
        self.report(line, column, error_message, where="")

    def report(self, line, column, error_message, where):
        print(f"[line: {line}, col: {column}] Error {where}: {error_message}", file=sys.stderr) # print to stderr so that the error messages are not mixed with the output of the program
        self.had_error = True

    def reset(self):
        self.had_error = False # one bad line in repl mode shouldnt stop the whole program, so im reseting the error flag.