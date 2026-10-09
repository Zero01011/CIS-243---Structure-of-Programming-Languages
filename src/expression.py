class Expression:
    """ this is the base class for every expression node"""
    def accept(self, visitor):
        # every node has to override this and call its own version
        raise NotImplementedError()

class BinaryExpression(Expression):
    """expression operator expression, like 1 + 3"""
    def __init__(self, left, operator, right):
        self.left = left # Expression
        self.operator = operator # Token, like PLUS or MINUS
        self.right = right # Expression

    def accept(self, visitor):
        return visitor.visit_binary_expression(self)

class UnaryExpression(Expression):
    """( "-" | "!" ) expression, like -1 or !treu"""

    def __init__(self, operator, right):
        self.operator = operator # Token, like bang or minus
        self.right = right # Expression

    def accept(self, visitor):
        return visitor.visit_unary_expression(self)

class GroupingExpression(Expression):
    """ '(' Expression ')', the parentheses arent stored, theyre implied by the node"""

    def __init__(self, expression):
        self.expression = expression # Expression

    def accept(self, visitor):
        return visitor.visit_grouping_expression(self)

class LiteralExpression(Expression):
    """A literal value, like a number or string"""

    def __init__(self, value):
        self.value = value # The literal value

    def accept(self, visitor):
        return visitor.visit_literal_expression(self)

    