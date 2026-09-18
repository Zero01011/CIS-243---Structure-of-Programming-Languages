import sys
from error_reporter import ErrorReporter
from scanner import Scanner

def main():
    arguments = sys.argv[1:] # the first arg is the script name, so ignore it
    if len(arguments) > 1:
        print("Woah, too many arguments bro!\nHere's how you do it: python src/nario.py [script]\nOr you can enter REPL mode: python src/nario.py", file=sys.stderr)
        sys.exit(1)
    elif len(arguments) == 1:
        file_mode(arguments[0])
    else:
        repl_mode()

def file_mode(script):
    reporter = ErrorReporter()
    try:
        with open(script, 'r', encoding='utf-8') as file:
            source_file = file.read()
    except OSError as error:
        print(f"Uh Oh! There was an error opening '{script}': {error}", file=sys.stderr)
        sys.exit(1)

    run(source_file, reporter)
    if reporter.had_error:
        sys.exit(1)

def repl_mode():
    reporter = ErrorReporter()
    while True:
        try:
            line = input("> ")
        except (KeyboardInterrupt, EOFError): # eof is mainly for piped input, but also ctrl+d on linux and ctrl+z on windows. And of course, keyboard is for ctrl+c
            print("\nSee ya later, alligator!")
            break
        run(line, reporter)
        reporter.reset()  # Reset the error flag for repl mode since an error shouldn't stop the whole thing.

def run(source_file, reporter):
    print(source_file)
    tokens = Scanner(source_file, reporter).scan_tokens()
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()