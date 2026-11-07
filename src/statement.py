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