# Lab 5 Report

## Setup/Dependencies
There are no dependencies. You can run from the repo root. The project uses Python.

**To run a test:** `python src/nario.py test/lab5/<test_file>`

## Design Choices
- Variable access before declaration
    - This is a runtime error like Lox. If it was a syntax error then later on functions wouldnt be able to use something that gets declared after them.
- Missing initializer
    - `var x;` is allowed but using x before it gets a value is a runtime error. I didnt want it to just be null like Lox since then if you forget to set it, it just prints null and you dont know why.
- Redeclaration
    - Its allowed in the same scope and it just replaces the old value like Lox, mostly so repl mode isnt annoying.
    - Declaring the same name inside a block makes a new variable that shadows the outer one.
- I also added `+=` and `-=`, so `x += 1` is the same as `x = x + 1`

## Testing
The test files are in `test/lab5/`

### variables.nario
`python src/nario.py test/lab5/variables.nario`
```
var a = 1;
var b = 2;
print a + b;
a = 5;
print a;
var later;
later = "set later";
print later;
var a = "redeclared";
print a;
var count = 10;
count += 5;
count -= 3;
print count;
```
output:
```
3
5
set later
redeclared
12
```

### scope.nario
`python src/nario.py test/lab5/scope.nario`
```
var a = "global a";
var b = "global b";
var c = "global c";
{
  var a = "outer a";
  var b = "outer b";
  {
    var a = "inner a";
    print a;
    print b;
    print c;
  }
  print a;
  print b;
  print c;
}
print a;
print b;
print c;
```
output:
```
inner a
outer b
global c
outer a
outer b
global c
global a
global b
global c
```
Every block gets its own scope, and when a variable is used it looks in the current scope first and then goes out one scope at a time until it finds it. So in the inner block `a` is the inner one, `b` comes from the outer block, and `c` is global. Once the inner block ends its scope is gone so `a` goes back to `outer a`, and after both blocks end everything is global again. The globals never changed since the blocks declared new variables instead of assigning to the old ones.

### syntax_errors.nario
`python src/nario.py test/lab5/syntax_errors.nario`
```
var a = 1;
var b = 2;
a + b = 3;
}
{
  print a;
```
output:
```
[line: 3, col: 7] Error at '=': Hey bro, the left side of '=' has to be a variable name.
[line: 4, col: 1] Error at '}': Broski, the '}' is missing its twin: '{', you gonna need that.
[line: 6, col: 11] Error on the last line: Hey bro, you got an opening brace at line 5, col 1 but no closing one, you gonna need that.
```

### undeclared_variable.nario
`python src/nario.py test/lab5/undeclared_variable.nario`
```
print x;
```
output:
```
[line: 1, col: 7] Error at 'x': Yo, 'x' was never declared, you gotta use 'var' first.
```

### uninitialized_variable.nario
`python src/nario.py test/lab5/uninitialized_variable.nario`
```
var x;
print x;
```
output:
```
[line: 2, col: 7] Error at 'x': My guy, 'x' doesn't have a value yet, you gotta give it one before using it.
```