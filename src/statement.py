class Statement:
    """ this will be the base class for every statement node, which is the same idea as the Expression class"""
    def accept(self, visitor):
        raise NotImplementedError()

class ExpressionStatement(Statement):
    """ this is a statement that just evaluates an expression, and discards the result"""
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_statement(self)

class PrintStatement(Statement):
    """ this is a statement that evaluates an expression and prints the result"""
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_print_statement(self)

class VarStatement(Statement):
    """ this is a statement that makes a new variable, the initializer is None if there was no assignment """
    def __init__(self, name, initializer):
        self.name = name # Token
        self.initializer = initializer # Expression or None

    def accept(self, visitor):
        return visitor.visit_var_statement(self)

class BlockStatement(Statement):
    """this is a statment that holds the statements inside {}, it gets its own scope"""
    def __init__(self, statements):
        self.statements = statements # list of Statements

    def accept(self, visitor):
        return visitor.visit_block_statement(self)