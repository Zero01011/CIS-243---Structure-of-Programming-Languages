from token_type import TokenType
from error_reporter import NarioRuntimeError
from environment import Environment, UNINITIALIZED

class Interpreter:
    """ evaluates the AST with a post order traversal, so the children are evaluated before the parent node"""
    def __init__(self, error_reporter):
        self.error_reporter = error_reporter
        self.environment = Environment() # starts as the global scope, changes when we go in and out of blocks

        
    def interpret(self, statements):
        """ runs every statement in order, and stops if there's a runtime error """
        try:
            for statement in statements:
                self.execute(statement)
        except NarioRuntimeError as error:
            # report the runtime error, this also catches the ones from environment.py
            self.error_reporter.report(error.token.line, error.token.column, error.message, f"at '{error.token.lexeme}'")

    def execute(self, statement):
        statement.accept(self)

    def visit_expression_statement(self, statement):
        self.evaluate(statement.expression) # statements do not give back a value, so the results just get thrown away

    def visit_print_statement(self, statement):
        value = self.evaluate(statement.expression)
        print(self.stringify(value)) 

    def visit_var_statement(self, statement):
        value = UNINITIALIZED # var x, with no initializer
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        self.environment.define(statement.name.lexeme, value)

    def visit_block_statement(self, statement):
        #a new scope that points back to the one we're in now
        self.execute_block(statement.statements, Environment(self.environment))

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            # this runseven if theres a runtime error, otherwise the repl would get stuck in the inner scope
            self.environment = previous

    def evaluate(self, expression):
        return expression.accept(self)

    def visit_literal_expression(self, expression):
        # the parser already stored the python value, so we just return it
        return expression.value
 
    def visit_variable_expression(self, expression):
        return self.environment.get(expression.name)

    def visit_assign_expression(self, expression):
        value = self.evaluate(expression.value)
        self.environment.assign(expression.name, value)
        return value # assignment is an expression, so print a = 2, prints 2

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
        """ make a NarioRuntimeError so we can raise it, interpret() reports it """
        return NarioRuntimeError(token, message)
 
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