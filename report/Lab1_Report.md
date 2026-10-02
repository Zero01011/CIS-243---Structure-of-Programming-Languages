# Lab 1 Report
### Language: Nario
### Extension: .nario

## Regex
- Numbers: `[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?`
- Strings: `"[^"]*"`
- Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`

## Design Choices 
- **Keywords**
    - I changed the function definiton cause I like pythons a bit more: `fun` -> `def`
    - I also changed nil for the same reason: `nil` -> `null`
- **Added Operators**
    - `%`
    - `+=`
    - `-=`
    - Because I added `+=` and `-=`, `-` and `+` are now one or two character tokens and need the lookahead for the same reason as `!`.
- **Nested block Comments**
    - I handled this by using a counter to count the depth. Every time we see `/*` 1 is added to the counter and every time we see `*/` 1 is subtracted from the counter. We consume everything until the counter is 0 and if EOF is reached with a counter > 0 then we throw an error. 
- **New errors**
    - A block comment that isnt closed.
    - Invalid scientific notation
    - A number too big  (`1e400`)
- **ASCII only**
    - I use an explict range when checking digits and letters, I dont use `isdigit()` and `isalpha()`, since those accept weird things. 

## Set-Up/Dependecies

There are no dependecies needed. You can run from the repo root. The project uses Python. 

**Repl mode**: `python src/nario.py`
- Ctrl+C to exit

**File mode**: `python src/nario.py test/lab1/all_tokens.nario`

## Testing
Test files are inside `test/lab1/`. Run each with `python src/nario.py test/lab1/<source>`. The Repl mode lines are in `test/lab1/repl_testing.md`.

| Purpose | Source | Expected | Scanner Output | Matched Expectations? |
|---|---|---|---|---|
| Test every token type and edge case | all_tokens.nario | All tokens, no errors, and nested comments are skipped. Edge cases: `+=-=!====<=>=`: takes the longes operator. `orchid`: is one identifier. `1.` -> turns into NUMBER DOT. `-7` -> turns into MINUS NUMBER | All tokens (110) with 0 errors. | Yes |
| Test every recoverable error | errors.nario | All 18 errors with the correct line and column. | 18 errors each with the correct line and column. And all 16 tokens are still scanned. | yes |
| Test a string that wasn't closed. It has its own file since it consumes the rest of the file. | open_string.nario | One error at line 1 column 3 which should be the opening quote. | 1 error at line 1 column 3 with tokens `(` and EOF. | Yes |
| Test an empty input file. | empty_file.nario | One EOF token. | A single EOF token. | Yes |
| Test a realistic program using all of the new stuff I added | test_program.nario | All tokens with no errors | All 62 tokens with no errors. | Yes | 
| Test too many arguments | 123.nario 456.nario | An error message telling you how to correctly use it. | The correct error message | Yes |
| Test a missing/non existent file | non_existent_file.nario | A file error message | The file error message | Yes |
| Test Repl mode. And make sure it keeps working even after errors. | repl_testing.md | Each error is reported, each token is displayed, and it keeps working after an error. | All 4 errors are displayed, the tokens are displayed, and it kept working after an error. | Yes |


## Known Limitations
- Repl mode only scans one line at a time, so strings and block comments cant be multi line. They work in files though.
- A string or block comment that isn't closed will swallow the rest of the file, and so anything after it wont be scanned
- Super small numbers like `1e-400` will become `0.0`

## Extra Credit 
**Nested Block Comments**: Lox didn't have block comments but Nario does. I used a depth counter since regex isn't an option. Now you can comment out code that already has a comment. This also creates a new error if a comment is never closed and the error gives you the location of the opening `/*`.
- Tests: `all_tokens.nario` (comments section) and `errors.nario` (open block comment)
- The error output: `[line: 16, col: 1] Error : Sooooo, one of your block comments wasn't closed.`

**Scientific Notatoin**: Scientific notation works and is allowed. So know `1e3`, `1E3`, `2.3e-3`, and `6.3E+2` are all valid. This also creates two new errors: invalid scientific notation and numbers that are too big. 
- Tests: `all_tokens.nario` (numbers section) and `errors.nario` (bad scientfic notation and too big)
- The error output:
    - `[line: 7, col: 1] Error : This ain't proper scientific notation big dawg: '1e'`
    - `[line: 12, col: 1] Error : That number is wayyyy too big broski: '1e400'.`