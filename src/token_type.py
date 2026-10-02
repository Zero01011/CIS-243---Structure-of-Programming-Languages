from enum import Enum, auto

class TokenType(Enum):
    # Single character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    PERCENT = auto() # I added this for modulo operator

    # one or two character tokens (these tokens need the lookahead)
    PLUS = auto() # moved this here because I am adding +=
    PLUS_EQUAL = auto() # I added this for += 
    MINUS = auto() # moved this here because I am adding -=
    MINUS_EQUAL = auto() # I added this for -=
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals and identifiers
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords (aka reserved words)
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    DEF = auto() # Lox uses fun I will be using def
    FOR = auto()
    FALSE = auto()
    IF = auto()
    NULL = auto() # Lox uses nil I will be using null
    OR = auto()
    RETURN = auto()
    TRUE = auto()
    PRINT = auto()
    SUPER = auto()
    THIS = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()

