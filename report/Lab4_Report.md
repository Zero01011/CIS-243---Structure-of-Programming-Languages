# Lab 4 Report

## Setup/Dependencies
There are no dependencies. You can run fro the repo root. The project uses Python.

**To run a test:** `python src/nario.py test/lab4/<test_file>`

## Testing
The test files are in `test/lab4/`

### test1.nario
`python src/nario.py test/lab4/test1.nario`
```
"one"
true;
print 2 +
```
output:
```
[line: 2, col: 1] Error at 'true': Hey bro, you need a ';' after the expression.
[line: 3, col: 10] Error on the last line: Sorry og, but I was expecting an expression here.
```
### test2.nario
`python src/nario.py test/lab4/test2.nario`
```
6 + 7;
print "Mario";
print true;
print 9 + 10;
print null;
```
output:
```
Mario
true
19
null
```