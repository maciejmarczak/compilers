#!/usr/bin/python
from collections import Set

from Ttype import ScopeType


class Symbol:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class VariableSymbol(Symbol):
    def __init__(self, name, type):
        Symbol.__init__(self, name, type)


class FunctionSymbol(Symbol):
    def __init__(self, name, type, args):
        Symbol.__init__(self, name, type)
        self.args_types = args
        self.has_return = False

    def found_return(self):
        self.has_return = True


class Scope(object):
    def __init__(self, parent, name):  # parent scope and symbol table name
        self.parent = parent
        self.name = name
        self.entry = dict()

    def put(self, name, symbol):  # put variable symbol or fundef under <name> entry
        self.entry[name] = symbol

    def get(self, name):  # get variable symbol or fundef from <name> entry
        return self.entry.get(name)

    def get_parent(self):
        return self.parent

    def find(self, name):
        if name in self.entry:
            return self.get(name)
        elif self.parent is not None:
            return self.parent.find(name)
        else:
            return None

    def find_scope(self, scope_name):
        if self.name == scope_name:
            return self
        elif self.parent is not None:
            return self.parent.find_scope(scope_name)
        else:
            return None


class SymbolTable:
    def __init__(self):
        self.current_scope = None
        self.current_type = None  # used for variable declarations
        self.fun_symbol = None
        self.labels = dict()

    def push_scope(self, name, fun=None):
        self.current_scope = Scope(self.current_scope, name)
        if name == ScopeType.FUNCTION:
            self.fun_symbol = fun

    def pop_scope(self):
        if self.current_scope.name == ScopeType.FUNCTION:
            self.fun_symbol = None
        self.current_scope = self.current_scope.get_parent()

    def put_label(self, name):
        self.labels[name] = name

    def has_label(self, name):
        return name in self.labels
