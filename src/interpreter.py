from token_type import TokenType

class NarioRuntimeError(Exception):
    """ gets raised on a runtime error, so we can jump out of every recrusive clal at one like the parser does"""

class Interpreter:
    """ evaluates the AST with a post order traversal, so the children are evaluated before the parent node"""
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter

        
    def interpret(self, expression):
        """ evalutest the expression and prints the rresult, or stops if there was a runtime error"""
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except NarioRuntimeError:
            return # the error was already reported, so just stop

    def evaluate(self, expression):
        return expression.accept(self)

    def visit_literal_expression(self, expression):
        # the parser already stored the python value, so we just return it
        return expression.value
 
    def visit_grouping_expression(self, expression):
        return self.evaluate(expression.expression)
 
    def visit_unary_expression(self, expression):
        right = self.evaluate(expression.right) # the operand has to be evaluated first
 
        if expression.operator.type == TokenType.MINUS:
            self.check_number(expression.operator, right)
            return -self.to_number(right)
        if expression.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
 
    def visit_binary_expression(self, expression):
        # left gets evaluated before right, so the operands go left to right
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)
        operator = expression.operator
 
        # equality doesnt give an error if the types dont match, its just false
        if operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
 
        # + is overloaded, so two strings will get concatenated
        if operator.type == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if self.is_number(left) and self.is_number(right):
                return self.to_number(left) + self.to_number(right)
            raise self.error(operator, "Bro, '+' needs two numbers or two strings, you cant mix them.")
 
        # the rest of the operators only work on numbers
        self.check_numbers(operator, left, right)
        left = self.to_number(left)
        right = self.to_number(right)
 
        if operator.type == TokenType.MINUS:
            return left - right
        if operator.type == TokenType.STAR:
            return left * right
        if operator.type == TokenType.SLASH:
            if right == 0:
                raise self.error(operator, "You cant divide by zero my guy.")
            return left / right
        if operator.type == TokenType.PERCENT:
            # % is basically division so it can divide by zero too
            if right == 0:
                raise self.error(operator, "My guyyy, you can't do modulo by zero.")
            return left % right
        if operator.type == TokenType.GREATER:
            return left > right
        if operator.type == TokenType.GREATER_EQUAL:
            return left >= right
        if operator.type == TokenType.LESS:
            return left < right
        if operator.type == TokenType.LESS_EQUAL:
            return left <= right
 
    # the helper functions
 
    @staticmethod
    def is_number(value):
        """ bools count as numbers because of the coercion. I cant just check for int since python already treats True as an int """
        if isinstance(value, float) or isinstance(value, bool):
            return True
        return False
 
    @staticmethod
    def to_number(value):
        """ the coercion, true becomes 1 and false becomes 0 """
        if value is True:
            return 1.0
        if value is False:
            return 0.0
        return value
 
    @staticmethod
    def is_truthy(value):
        """ null, false, and 0 are false, since 0 <-> false. everything else is true like lox """
        if value is None or value is False:
            return False
        if isinstance(value, float) and value == 0:
            return False
        return True
 
    def is_equal(self, left, right):
        # numbers and bools get compared as numbers so 1 == true is true
        if self.is_number(left) and self.is_number(right):
            return self.to_number(left) == self.to_number(right)
        # if the types are different its just false, so "1" == 1 is false
        if type(left) != type(right):
            return False
        return left == right
 
    def check_number(self, operator, operand):
        if not self.is_number(operand):
            raise self.error(operator, f"'{operator.lexeme}' only works on numbers my guy.")
 
    def check_numbers(self, operator, left, right):
        if not self.is_number(left) or not self.is_number(right):
            raise self.error(operator, f"Both sides of '{operator.lexeme}' gotta be numbers my guy.")
 
    def error(self, token, message):
        """ report the runtime error at the operator and return a NarioRuntimeError so we can raise it """
        self.error_reporter.report(token.line, token.column, message, f"at '{token.lexeme}'")
        return NarioRuntimeError()
 
    @staticmethod
    def stringify(value):
        """ turns the python value into how it should look in nario """
        if value is None:
            return "null"
        # check booleans before numbers since python treats True as 1
        if isinstance(value, bool):
            if value is True:
                return "true"
            if value is False:
                return "false"
        if isinstance(value, float):
            # every number is a float, so 7 would show up as 7.0, so this drops the .0
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return value # strings print without the quotes