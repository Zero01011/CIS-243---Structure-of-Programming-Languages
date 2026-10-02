import math

from token_type import TokenType
from nario_token import Token

# a dict mapping the single character tokens to their token types
SINGLE_CHAR_TOKENS = {
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    '{': TokenType.LEFT_BRACE,
    '}': TokenType.RIGHT_BRACE,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
    ';': TokenType.SEMICOLON,
    '*': TokenType.STAR,
    '%': TokenType.PERCENT,
}

# tokens that may be followed by '=' creating a two character token
ONE_OR_TWO_CHAR_TOKENS = {
    '+': (TokenType.PLUS, TokenType.PLUS_EQUAL),
    '-': (TokenType.MINUS, TokenType.MINUS_EQUAL),
    '!': (TokenType.BANG, TokenType.BANG_EQUAL),
    '=': (TokenType.EQUAL, TokenType.EQUAL_EQUAL),
    '>': (TokenType.GREATER, TokenType.GREATER_EQUAL),
    '<': (TokenType.LESS, TokenType.LESS_EQUAL),
}

# the characters the scanner skips over, \n will still be counted for line nums
WHITESPACE = [' ', '\r', '\t', '\n']

# our reserved words, scanned as identifiers, but then checked against this dict to see if they are reserved words
KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "def": TokenType.DEF, # lox used fun, but I will be using def
    "for": TokenType.FOR,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "null": TokenType.NULL, #lox used nil, but I will be using null
    "or": TokenType.OR,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "print": TokenType.PRINT,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}

class Scanner:
    def __init__(self, source, error_reporter):
        self.source = source
        self.error_reporter = error_reporter
        self.tokens = []
        self.start = 0 # the index of the first character in the current lexeme
        self.current = 0 # the index of the character that is about to be read
        # the location of the character to be read, so that we can report errors with line and column numbers
        self.line = 1 
        self.column = 1
        # the location of the first character in the current lexeme, so that we can report errors with line and column numbers
        self.start_line = 1
        self.start_column = 1

    def scan_tokens(self):
        """The main loop of the scanner, scans one token at a time until the end of the source is reached"""
        while not self.is_at_end():
            # start of the next lexeme
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column)) # finish with EOF so the parser will know where input stops

        return self.tokens


    def scan_token(self):
        """ Scans a single token, and adds it to the list of tokens. If the token is not recognized, it reports an error."""
        character = self.consume()

        if character in SINGLE_CHAR_TOKENS:
            self.create_token(SINGLE_CHAR_TOKENS[character])
        elif character in ONE_OR_TWO_CHAR_TOKENS:
            single, double = ONE_OR_TWO_CHAR_TOKENS[character]
            if self.match_consume('='):
                self.create_token(double)
            else:
                self.create_token(single)
        elif character == '/':
            if self.match_consume('/'):
                self.line_comment()
            elif self.match_consume('*'):
                self.block_comment()
            else:
                self.create_token(TokenType.SLASH)
        elif character in WHITESPACE:
            pass # ignore any whitespace
        elif character == '"': 
            self.scan_string()
        elif self.is_digit(character):
            self.scan_number()
        elif self.start_is_alpha(character):
            self.scan_identifier()
        else:
            self.error(f"WOAH! That's not a character I was expecting: '{character}'")

    # helper functions
    def is_at_end(self):
        if self.current >= len(self.source):
            return True
        return False

    def consume(self):
        character = self.source[self.current]
        self.current += 1
        if character == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return character

    def create_token(self, type, literal=None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(type, lexeme, literal, self.start_line, self.start_column))

    def error(self, message):
        self.error_reporter.error(self.start_line, self.start_column, message)

    def match_consume(self, expected):
        """consumes the next character if it matches the expected character"""
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.consume() 
        return True

    def peek(self):
        """ return the next character but WITHOUT consuming it"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        """ return the next next character but WITHOUT consuming it"""
        if (self.current + 1) >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def line_comment(self):
        """" skip over the rest of the line, since its a comment"""
        while self.peek() != '\n' and not self.is_at_end():
            self.consume()

    def block_comment(self):
        """ skips over the block comment, this comment can be a multi-line comment, and can be nested, 
        so each time we see /* we increment, and each time we see */ we decrement, and when we reach 0 we are done"""
        depth = 1
        while depth > 0:
            if self.is_at_end():
                self.error("Sooooo, one of your block comments wasn't closed.")
                return
            if self.peek() == '/' and self.peek_next() == '*': # if we see /* we increment depth
                self.consume()
                self.consume()
                depth += 1
            elif self.peek() == '*' and self.peek_next() == '/': # if we see */ we decrement depth
                self.consume()
                self.consume()
                depth -= 1
            else:
                self.consume() # otherwise we just consume the character and keep going

    def scan_string(self):
        """ scan a string literal, and since the starting " has been consumed, we will keep consuming until we see the closing " or reach the end"""
        while self.peek() != '"' and not self.is_at_end():
            self.consume()

        if self.is_at_end():
            self.error("My man, come on, you forgot a closing quote on one of your strings.")
            return

        self.consume() # consume the closing "
        # now lets trim the quotes
        value = self.source[self.start + 1 : self.current - 1] # trim the quotes
        self.create_token(TokenType.STRING, value)

    @staticmethod # not using self as an arg, so we need this
    def is_digit(character):
        """ check if the character is a digit. not using str.isdigit() because it returns True for unicode digits, and we only want 0-9"""
        if character >= '0' and character <= '9':
            return True
        return False

    def scan_number(self):
        # whole number digits
        while self.is_digit(self.peek()):
            self.consume()

        # check for decimal point, if a digit is after it consume it, otherwise if there is no digit after it it becomes a DOT token
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.consume() # consume the decimal point
            while self.is_digit(self.peek()):
                self.consume()

        # check for scientific notations, if there is e/E a digit MUST follow it
        if self.peek() in ['e', 'E']:
            self.consume() # consume the e/E
            if self.peek() in ['+', '-']: # optional + or - sign
                self.consume()
            if not self.is_digit(self.peek()): # if there is no digit after the e/E, its an error
                problem = self.source[self.start:self.current] # the lexeme that caused the problem
                self.error(f"This ain't proper scientific notation big dawg: '{problem}'")
                return
            while self.is_digit(self.peek()):
                self.consume()

        lexeme = self.source[self.start:self.current]
        value = float(lexeme) # convert the lexeme to a float, since it can be a whole number or a decimal number
        if math.isinf(value):
            self.error(f"That number is wayyyy too big broski: '{lexeme}'.")
            return
        self.create_token(TokenType.NUMBER, value)

    @staticmethod
    def start_is_alpha(character):
        """return true for letters a-z and A-Z, and also '_'. These are the characters an identifier can start with"""
        if ('a' <= character <= 'z') or ('A' <= character <= 'Z') or character == '_':
            return True
        return False

    @staticmethod
    def rest_is_alphanumeric(character):
        """return true for letters and numbers after the first character of an idetifer"""
        if Scanner.start_is_alpha(character) or Scanner.is_digit(character):
            return True
        return False
    
    def scan_identifier(self):
        """scan an identifier/keyword. The regex for that is [a-zA-Z_][a-zA-Z0-9_]*
            this will use a maximal munch. Aka the longest possible lexeme wins"""
        while self.rest_is_alphanumeric(self.peek()):
            self.consume()

        text = self.source[self.start:self.current]
        # its a keyword if its in the table, otherwise its a plain identifier
        self.create_token(KEYWORDS.get(text, TokenType.IDENTIFIER))
