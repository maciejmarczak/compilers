from collections import defaultdict


class Types:
    INT = 'int'
    STRING = 'string'
    FLOAT = 'float'


class ScopeType:
    GLOBAL = 'global_scope'
    FUNCTION = 'function_scope'
    LOOP = 'loop_scope'
    NESTED = 'nested'


class MemoryType:
    FUNCTION = 'function_memory'
    GLOBAL = 'global_memory'
    NESTED = 'nested_memory'


arithmetic_operators = ['+', '-', '*', '/']
relation_operators = ['<', '<=', '>', '>=', '==', '!=']
binary_operators = ['||', '&&', '|', '^', '&', '<<', '>>']


class Ttype:
    def __init__(self):
        self.ttype = self.nested_dict(3, str)

        for operator in arithmetic_operators + binary_operators + relation_operators + ['=', '%']:
            self.ttype[operator][Types.INT][Types.INT] = Types.INT

        for operator in arithmetic_operators:
            self.ttype[operator][Types.FLOAT][Types.FLOAT] = Types.FLOAT
            self.ttype[operator][Types.FLOAT][Types.INT] = Types.FLOAT
            self.ttype[operator][Types.INT][Types.FLOAT] = Types.FLOAT

        for operator in relation_operators:
            self.ttype[operator][Types.STRING][Types.STRING] = Types.INT
            self.ttype[operator][Types.FLOAT][Types.FLOAT] = Types.INT
            self.ttype[operator][Types.FLOAT][Types.INT] = Types.INT
            self.ttype[operator][Types.INT][Types.FLOAT] = Types.INT

        self.ttype['='][Types.STRING][Types.STRING] = Types.STRING
        self.ttype['='][Types.FLOAT][Types.FLOAT] = Types.FLOAT
        self.ttype['='][Types.INT][Types.FLOAT] = Types.INT
        self.ttype['='][Types.FLOAT][Types.INT] = Types.FLOAT

        self.ttype['+'][Types.STRING][Types.STRING] = Types.STRING
        self.ttype['*'][Types.STRING][Types.INT] = Types.STRING

    def nested_dict(self, n, type_name):
        if n == 1:
            return defaultdict(type_name)
        else:
            return defaultdict(lambda: self.nested_dict(n - 1, type_name))

    def get_type(self, op, left, right):
        return self.ttype[op][left][right]
