class Token:
    """Represents a token, its a lexeme with its extra info"""

    def __init__(self, type, lexeme, literal, line, column):
        self.type = type # the type of the token, like keyword or identifier
        self.lexeme = lexeme # the actual string of the token
        self.literal = literal # the actual value of the token, will be None for keywords and identifiers
        self.line = line # the line number of the token for error reporting
        self.column = column # same situation as line

    def __str__(self):
        return f"{self.type} | {self.lexeme} | {self.literal}"

    def __repr__(self):
        """So i can print the token in a list and it will look nice"""
        return self.__str__()