from error_reporter import NarioRuntimeError

#var x; gets this instead of null so we know it never got a value assigned
UNINITIALIZED = object()

class Environment:
    """ stores the variables for one scope, enclosing is the scope around it, or None for the global scope"""
    def __init__(self, enclosing=None):
        self.values = {} # the key is the var name (lexeme) not the token
        self.enclosing = enclosing

    def define(self, name, value):
        #redclaring is allowed, its just replaces the old value
        self.values[name] = value

    def get(self, name):
        #check this scope first, then keep going until the global scope
        if name.lexeme in self.values:
            value = self.values[name.lexeme]
            if value is UNINITIALIZED:
                raise NarioRuntimeError(name, f"My guy, '{name.lexeme}' doesn't have a value yet, you gotta give it one before using it.")
            return value
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise NarioRuntimeError(name, f"Yo, '{name.lexeme}' was never declared, you gotta use 'var' first.")

    def assign(self, name, value):
        # same search as get, but assigning never makes a new variable
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise NarioRuntimeError(name, f"Yo, '{name.lexeme}' was never declared, you gotta use 'var' first.")