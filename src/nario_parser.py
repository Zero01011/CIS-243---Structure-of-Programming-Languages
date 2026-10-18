from token_type import TokenType
from expression import BinaryExpression, UnaryExpression, GroupingExpression, LiteralExpression

# the binary operators that can never start an expression, except minus (-) since it can be unary
BINARY_OPERATORS = (
    TokenType.PLUS,
    TokenType.STAR,
    TokenType.SLASH,
    TokenType.PERCENT,
    TokenType.EQUAL_EQUAL,
    TokenType.BANG_EQUAL,
    TokenType.GREATER,
    TokenType.GREATER_EQUAL,
    TokenType.LESS,
    TokenType.LESS_EQUAL,
)

class ParsingError(Exception):
    """ raised on an syntax error, wo we can jump out of every recursive call at once  """

class Parser:
    """ the recursive descent parser, each grammar rule is its own method:
    expression -> equality ;
    equality -> comparison ( ( "!=" | "==" ) comparison )* ;
    comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term -> factor ( ( "-" | "+" ) factor )* ;
    factor -> unary ( ( "/" | "*" | "%" ) unary )* ;
    unary -> ( "!" | "-" ) unary | primary ;
    primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" ;
    """

    def __init__(self, tokens, error_reporter):
        self.tokens = tokens # the list of the tokens from the scanner, which always ends with EOF
        self.error_reporter = error_reporter
        self.current = 0 # this will be the index of the token that is aboubt to be parsed

    def parse(self):
        """ this will parse exactly one expression. IT will return the AST, or NOne if there was a syntax error """
        try:
            expression = self.expression()
            # only one expresssion per input so that anything left over (besided EOF) will be an error
            if not self.is_at_end():
                if self.check(TokenType.RIGHT_PAREN):
                    raise self.error(self.peek(), "Broski, the ')' is missing its twin: '(', you gonna need that.")
                raise self.error(self.peek(), "Sorry bro, but I can only parse one expression at a time, you gotta clean up the extra stuff after the first expression.")
            return expression
        except ParsingError:
            return None # the error has already been reported so we can just stop parsing\
        # This is to catch the stuff like (((((((((...1...))))))))) that is nested thousands of levels since it will break Ptyhons call stack and give an actual RecursionError instead of a ParsingError, so we can actually report it nicely isntead of crashing
        except RecursionError:
            self.error(self.peek(), "WOAHHH, you got some crazy deep nesting going on here, can you clean that up a bit? I can't handle that much recursion XD.")
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        # the * in the grammar will become the while loop, the tree from the last loop becomes the left operand of the next one, which makes this left associative
        expression = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def comparison(self):
        expression = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def term(self):
        expression = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def factor(self):
        # the % operator is the same precedence as * and /
        expression = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT):
            operator = self.previous()
            right = self.unary()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def unary(self):
        # unary calls itself for its operans, so that means --1 is (- (- 1)), which makes it right associative
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpression(operator, right)
        return self.primary()

    def primary(self):
        # the base case of the recursion
        if self.match(TokenType.FALSE):
            return LiteralExpression(False)
        if self.match(TokenType.TRUE):
            return LiteralExpression(True)
        if self.match(TokenType.NULL):
            return LiteralExpression(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpression(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            opening = self.previous() # store the opening parenthesis so we can point to it in the error, like the block comment error
            expression = self.expression()
            self.expect(TokenType.RIGHT_PAREN, f"Hey bro, you got an opening parenthesis at line {opening.line}, col {opening.column} but no closing one, you gonna need that.")
            return GroupingExpression(expression)
        # check for the binary operators 
        if self.peek().type in BINARY_OPERATORS:
            operator = self.peek()
            raise self.error(operator, f"Broooooo, the '{operator.lexeme}' is missing its left operand, it needs something before it.")
        raise self.error(self.peek(), "Sorry og, but I was expecting an expression here.")


    # the helper functions

    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.consume()
                return True
        return False

    def check(self, token_type):
        """ check if the next token is of the given type, but doesnt consume it"""
        if self.is_at_end():
            return False
        if self.peek().type == token_type:
            return True
        return False

    def consume(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def expect(self, token_type, message):
        """ if the next token is of the type we need, consume it, otherwise its a syntx error"""
        if self.check(token_type):
            return self.consume()
        raise self.error(self.peek(), message)

    def is_at_end(self):
        if self.peek().type == TokenType.EOF:
            return True
        return False

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        """ report an error at the tokens location and return a ParsingError so we can raise it later"""
        if token.type == TokenType.EOF:
            where = "on the last line"
        else:
            where = f"at '{token.lexeme}'"
        self.error_reporter.report(token.line, token.column, message, where)

        return ParsingError() # we return this so we can raise it later, but we dont raise it here because we want to report the error first

        