# Lab 2 Report

## Expression Grammar
```
expression -> literal
            | unary
            | binary
            | grouping;

literal     -> NUMBER | STRING | "true" | "false" | "null" ;
grouping    -> "(" expression ")" ;
unary       -> ( "-" | "!" ) expression ;
binary      -> expression operator expression ;
operator    -> "==" | "!=" | "<" | "<=" | ">" | ">=" | "+" | "-" | "*" | "/" | "%" ;
```

**Literal types:** numbres (whole, decimal, and scientific notation, are all stored as floats), strings, `true`, `false`, and `null`.

**Unary operators:** `-` (negate) and `!` (not).

**Binary Operators:** equality `==` `!=`, comparision `<` `<=` `>` `>=`, and arithmetic `+` `-` `*` `/` `%`.

## Design choices compared to Lox
- **Keywords**
    - Same as Lab 1: `nil` -> `null`, so the literal rule uses `"null"`
- **Added Operators**
    - `%` is a binary operator. When I write the parser it will go in the same precedence level as `*` and `/`
    - `+=` and `-=` are not in the expression grammar, instead they are assignment operators, and Lox adds assignment later as its own rule, so for now they only exist in the scanner.
- **Literal Nodes**
    - The slides say a literal's value should be a token but the slide example uses `Literal(123)`, so I followed the example, meaning literal nodes store the value and not the token. 
- **Printing Literals**
    - Strings print with quotes (`"1"`). Lox prints them without quotes, I changed this cause then `"1"` and `1` would look the same, and each printed string should only match one tree.
    - Whole numbers print without `.0`. My scanner stores every number as a float, so `123` would print as `123.0`. The printer cuts off the `.0`.
- **Visitor Pattern**
    - The slides showed two ways to do this, I decided to use the visitor pattern. The node classes in `expresion.py` only store data, and `AST_printer.py` walks the tree. This keeps the printing code out of the node classes.
- **Tokens**
    - My tokens take a column as well as a line, so it's `Token(TokenType.MINUS, "-", None, 1, 1)`.
## Setup/Dependencies
There are no dependecies needed. You can run from the repo root. The project uses Python. 
 
`python test/lab2/AST_printer_tests.py`
 
New files: `src/expression.py` (AST classes), `src/AST_printer.py` (printer), `test/lab2/AST_printer_tests.py` (hard-coded ASTs). The Lab 1 files in `src/` are reused for `Token` and `TokenType`.
 
## Testing
Each rows hard-coded AST is built in the matching section of `test/lab2/AST_printer_tests.py`. For example, test 1:
```python
BinaryExpression(
    UnaryExpression(MINUS, LiteralExpression(123.0)),
    STAR,
    GroupingExpression(LiteralExpression(45.67)),
)
```
 
| # | Purpose | Hard-coded AST | Expected output | Actual printer output | Matched Expectations? |
|---|---|---|---|---|---|
| 1 | Rubric example | `-123 * (45.67)` | `(* (- 123) (group 45.67))` | same | Yes |
| 2 | Every literal type | `7`, `69.42`, `6.3E+2`, `2.3e-3`, `"Nario"`, `true`, `false`, `null` | `7`, `69.42`, `630`, `0.0023`, `"Nario"`, `true`, `false`, `null` | same | Yes |
| 3 | Arithmetic operators and nesting | `1 + 2 * 3 - 4` | `(- (+ 1 (* 2 3)) 4)` | same | Yes |
| | | `1 + 2 * (3 - 4)` | `(+ 1 (* 2 (group (- 3 4))))` | same | Yes |
| | | `10 / 4 % 3` | `(% (/ 10 4) 3)` | same | Yes |
| 4 | Comparison and equality operators | `1 - (2 * 3) < 4 == false` | `(== (< (- 1 (group (* 2 3))) 4) false)` | same | Yes |
| | | `1 <= 2 != 3 > 2` | `(!= (<= 1 2) (> 3 2))` | same | Yes |
| | | `"mario" <= "Nario" == !false` | `(== (<= "mario" "Nario") (! false))` | same | Yes |
| 5 | Unary operators, stacked unary, unary on a group | `-43`, `!null`, `!!true`, `-(-5)`, `!(1 == 2)` | `(- 43)`, `(! null)`, `(! (! true))`, `(- (group (- 5)))`, `(! (group (== 1 2)))` | same | Yes |
| 6 | Edge cases: triple group, string vs number, empty string, parens inside a string, binary minus next to unary minus | `(((0)))`, `"1" + 1`, `""`, `"a (b) c"`, `1 - -1` | `(group (group (group 0)))`, `(+ "1" 1)`, `""`, `"a (b) c"`, `(- 1 (- 1))` | same | Yes |
 
## Known Limitations
- There is no parser yet, so trees are built by hand and nothing stops you from building a tree the grammar wouldn't produce (like `UnaryExpression` with a `+` token).
- Very big or very small numbers print in Python's format (`1e+20`), not the way they were typed.
- Strings print with plain quotes, so a string containing a `"` would look wrong. My scanner doesn't support escaped quotes, so a string can't contain one yet.
 
