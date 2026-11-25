from token_type import TokenType
from nario_token import Token
from expression import BinaryExpression, UnaryExpression, GroupingExpression, LiteralExpression, VariableExpression, AssignExpression
from statement import ExpressionStatement, PrintStatement, VarStatement, BlockStatement

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

# keywords that start a statement, meaning they are safe places to pick back up after an erorr
# the only statment right now is print, the rest are preparing for later labs
STATEMENT_KEYWORDS = (
    TokenType.PRINT,
    TokenType.CLASS,
    TokenType.DEF,
    TokenType.VAR,
    TokenType.FOR,
    TokenType.WHILE,
    TokenType.IF,
    TokenType.RETURN,
)

class ParsingError(Exception):
    """ raised on an syntax error, wo we can jump out of every recursive call at once  """

class Parser:
    """ the recursive descent parser, each grammar rule is its own method:
    program -> declaration* EOF ;
    declaration -> var_declaration | statement ;
    var_declaration -> "var" IDENTIFIER ( "=" expression )? ";" ;
    statement -> expression_statement | print_statement | block ;
    expression_statement -> expression ";" ;
    print_statement -> "print" expression ";" ;
    block -> "{" declaration* "}" ;
    expression -> assignment ;
    assignment -> IDENTIFIER ( "=" | "+=" | "-=" ) assignment | equality ;
    equality -> comparison ( ( "!=" | "==" ) comparison )* ;
    comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term -> factor ( ( "-" | "+" ) factor )* ;
    factor -> unary ( ( "/" | "*" | "%" ) unary )* ;
    unary -> ( "!" | "-" ) unary | primary ;
    primary -> NUMBER | STRING | "true" | "false" | "null" | "(" expression ")" | IDENTIFIER ;
    """

    def __init__(self, tokens, error_reporter):
        self.tokens = tokens # the list of the tokens from the scanner, which always ends with EOF
        self.error_reporter = error_reporter
        self.current = 0 # this will be the index of the token that is aboubt to be parsed

    def parse(self):
        """ parse the declarations until the end of the file. Returns a list of statements that parsed without errors """
        statements = []
        while not self.is_at_end():
            try:
                statement = self.declaration()
            except RecursionError:
                self.error(self.peek(), "WOAHHH, you got some crazy deep nesting going on here, clean that up man, it's too much recursion.")
                self.panic_mode()
                continue
            if statement is not None:
                statements.append(statement)
        return statements

    def declaration(self):
        # a } here means there was no { for it, since a block would have used it up
        if self.check(TokenType.RIGHT_BRACE):
            self.error(self.peek(), "Broski, the '}' is missing its twin: '{', you gonna need that.")
            self.consume()
            return None
        # try is her so errors inside a block get ahndled inside the block
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParsingError:
            self.panic_mode() # the error was already reported, so we can just skip to the next statement
            return None

    def var_declaration(self):
        name = self.expect(TokenType.IDENTIFIER, "Yo, you need a variable name after 'var'.")
        initializer = None # stays None for var x; so the interpreter knows it doesnt have a value yet
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.expect_semicolon("Yo, you need a ';' after the variable declaration.")
        return VarStatement(name, initializer)

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        return self.expression_statement()

    def block(self):
        opening = self.previous() # store the { so the missing } error can point back to it, like the parenthesis error
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statement = self.declaration()
            if statement is not None:
                statements.append(statement)
        self.expect(TokenType.RIGHT_BRACE, f"Hey bro, you got an opening brace at line {opening.line}, col {opening.column} but no closing one, you gonna need that.")
        return BlockStatement(statements)

    def print_statement(self):
        value = self.expression()
        self.expect_semicolon("Yo, you need a ';' after the value you're printing.")
        return PrintStatement(value)

    def expression_statement(self):
        expression = self.expression()
        self.expect_semicolon("Hey bro, you need a ';' after the expression.")
        return ExpressionStatement(expression)

    def expect_semicolon(self, message):
        # an extra ) shows up right where the ; should be, so it still gets its own error message
        if self.check(TokenType.RIGHT_PAREN):
            raise self.error(self.peek(), "Broski, the ')' is missing its twin: '(', you gonna need that.")
        self.expect(TokenType.SEMICOLON, message)

    def panic_mode(self):
        """ skip the tokens until we're probably at the start of the next statement """
        while not self.is_at_end():
            if self.check(TokenType.RIGHT_BRACE):
                return # dont skip a }, the block it closes still needs it
            self.consume() # skip the token that caused the error
            if self.previous().type == TokenType.SEMICOLON:
                return # we found the end of the statement, so we can stop skipping
            if self.peek().type in STATEMENT_KEYWORDS:
                return # we found the start of a statement, so we can stop skipping

    def expression(self):
        return self.assignment()

    def assignment(self):
        # parse the left side first, we dont know its an assignment until we see =
        expression = self.equality()
        if self.match(TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL):
            operator = self.previous()
            value = self.assignment() # calls itself so a = b = 1 is a = (b = 1), right associative
            if isinstance(expression, VariableExpression):
                if operator.type == TokenType.EQUAL:
                    return AssignExpression(expression.name, value)
                # x += 1 turns into x = x + 1, and x -= 1 turns into x = x - 1
                if operator.type == TokenType.PLUS_EQUAL:
                    math_type = TokenType.PLUS
                else:
                    math_type = TokenType.MINUS
                math_operator = Token(math_type, operator.lexeme, None, operator.line, operator.column) # use += as the lexeme so the error shows +=
                return AssignExpression(expression.name, BinaryExpression(expression, math_operator, value))
            # just report it, no need to panic since the parser still knows where it is
            self.error(operator, f"Hey bro, the left side of '{operator.lexeme}' has to be a variable name.")
        return expression

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
        if self.match(TokenType.IDENTIFIER):
            return VariableExpression(self.previous())
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