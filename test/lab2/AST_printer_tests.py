import os
import sys
# add the src directory to the sys.path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from token_type import TokenType
from nario_token import Token
from expression import BinaryExpression, UnaryExpression, GroupingExpression, LiteralExpression
from AST_printer import ASTPrinter

printer = ASTPrinter()

def token(type, lexeme):
    """create an operator token, the line/column are just 1 since there hard coded"""
    return Token(type, lexeme, None, 1, 1)

# operator tokens, so the trees can be readable
PLUS = token(TokenType.PLUS, "+")
MINUS = token(TokenType.MINUS, "-")
STAR = token(TokenType.STAR, "*")
SLASH = token(TokenType.SLASH, "/")
PERCENT = token(TokenType.PERCENT, "%")
BANG = token(TokenType.BANG, "!")
EQUAL_EQUAL = token(TokenType.EQUAL_EQUAL, "==")
BANG_EQUAL = token(TokenType.BANG_EQUAL, "!=")
LESS = token(TokenType.LESS, "<")
LESS_EQUAL = token(TokenType.LESS_EQUAL, "<=")
GREATER = token(TokenType.GREATER, ">")
GREATER_EQUAL = token(TokenType.GREATER_EQUAL, ">=")

def check(number, nario_code, tree):
    """ prints the nario code the tree stands for and then what the printer made from it"""
    print(f"[{number}] {nario_code}")
    print(f"    -> {printer.print(tree)}")

# numbers are floats since that is what the scanner gives us (123 -> 123.0)

print("1. Rubric Example") # The example AST from chapter 6 slide 43
check(1, "-123 * (45.67)", BinaryExpression(
    UnaryExpression(MINUS, LiteralExpression(123.0)),
    STAR,
    GroupingExpression(LiteralExpression(45.67))
))

print("\n2. Every literal type")
check(2, "7", LiteralExpression(7.0))
check(2, "69.42", LiteralExpression(69.42))
check(2, "6.3E+2", LiteralExpression(630.0))
check(2, "2.3e-3", LiteralExpression(0.0023))
check(2, '"Nario"', LiteralExpression("Nario"))
check(2, "true", LiteralExpression(True))
check(2, "false", LiteralExpression(False))
check(2, "null", LiteralExpression(None))

print("\n3. Arithmetic operators and nesting")
check(3, "1 + 2 * 3 - 4", BinaryExpression(
    BinaryExpression(LiteralExpression(1.0), PLUS, BinaryExpression(LiteralExpression(2.0), STAR, LiteralExpression(3.0))),
    MINUS,
    LiteralExpression(4.0),
))
check(3, "1 + 2 * (3 - 4)", BinaryExpression(
    LiteralExpression(1.0),
    PLUS,
    BinaryExpression(LiteralExpression(2.0), STAR, GroupingExpression(BinaryExpression(LiteralExpression(3.0), MINUS, LiteralExpression(4.0)))),
))
check(3, "10 / 4 % 3", BinaryExpression(
    BinaryExpression(LiteralExpression(10.0), SLASH, LiteralExpression(4.0)),
    PERCENT,
    LiteralExpression(3.0),
))
 
print("\n4. Comparison and equality operators")
check(4, "1 - (2 * 3) < 4 == false", BinaryExpression(
    BinaryExpression(
        BinaryExpression(LiteralExpression(1.0), MINUS, GroupingExpression(BinaryExpression(LiteralExpression(2.0), STAR, LiteralExpression(3.0)))),
        LESS,
        LiteralExpression(4.0),
    ),
    EQUAL_EQUAL,
    LiteralExpression(False),
))
check(4, "1 <= 2 != 3 > 2", BinaryExpression(
    BinaryExpression(LiteralExpression(1.0), LESS_EQUAL, LiteralExpression(2.0)),
    BANG_EQUAL,
    BinaryExpression(LiteralExpression(3.0), GREATER, LiteralExpression(2.0)),
))
check(4, '"mario" <= "Nario" == !false', BinaryExpression(
    BinaryExpression(LiteralExpression("mario"), LESS_EQUAL, LiteralExpression("Nario")),
    EQUAL_EQUAL,
    UnaryExpression(BANG, LiteralExpression(False)),
))
 
print("\n5. Unary operators")
check(5, "-43", UnaryExpression(MINUS, LiteralExpression(43.0)))
check(5, "!null", UnaryExpression(BANG, LiteralExpression(None)))
check(5, "!!true", UnaryExpression(BANG, UnaryExpression(BANG, LiteralExpression(True))))
check(5, "-(-5)", UnaryExpression(MINUS, GroupingExpression(UnaryExpression(MINUS, LiteralExpression(5.0)))))
check(5, "!(1 == 2)", UnaryExpression(BANG, GroupingExpression(BinaryExpression(LiteralExpression(1.0), EQUAL_EQUAL, LiteralExpression(2.0)))))
 
print("\n6. Edge cases")
check(6, "(((0)))", GroupingExpression(GroupingExpression(GroupingExpression(LiteralExpression(0.0)))))
check(6, '"1" + 1', BinaryExpression(LiteralExpression("1"), PLUS, LiteralExpression(1.0)))
check(6, '""', LiteralExpression(""))
check(6, '"a (b) c"', LiteralExpression("a (b) c"))
check(6, "1 - -1", BinaryExpression(LiteralExpression(1.0), MINUS, UnaryExpression(MINUS, LiteralExpression(1.0))))
    