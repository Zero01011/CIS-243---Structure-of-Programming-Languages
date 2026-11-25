class ASTPrinter:
 
    def print(self, expression):
        return expression.accept(self)
 
    def visit_binary_expression(self, expression):
        return self.wrap(expression.operator.lexeme, expression.left, expression.right)
 
    def visit_unary_expression(self, expression):
        return self.wrap(expression.operator.lexeme, expression.right)
 
    def visit_grouping_expression(self, expression):
        return self.wrap("group", expression.expression)
 
    def visit_literal_expression(self, expression):
        return self.stringify(expression.value)
 
    def visit_variable_expression(self, expression):
        return expression.name.lexeme

    def visit_assign_expression(self, expression):
        # the name is a token, not a node, so it cant go through wrap
        return f"(= {expression.name.lexeme} {expression.value.accept(self)})"

    def wrap(self, name, *children):
        """puts the name and every child (printed recursively) inside one set of parentheses"""
        printed_children = " ".join(child.accept(self) for child in children)
        return f"({name} {printed_children})"
 
    @staticmethod
    def stringify(value):
        """how a literal's python value should look in nario"""
        if value is None:
            return "null"
        # we check booleans before numbers since python treats True as 1
        if isinstance(value, bool):
            if value is True:
                return "true"
            if value is False:
                return "false"
        if isinstance(value, str):
            # keep the quotes, otherwise "10" and 10 would print the exact same
            return f'"{value}"'
        # every number from the scanner is a float, so 7 would show up as 7.0, so this drops the .0
        text = str(value)
        if text.endswith(".0"):
            text = text[:-2]
        return text