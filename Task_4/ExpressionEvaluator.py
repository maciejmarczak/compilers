
class ExpressionEvaluator:
    def __init__(self):
        self.expressions = {'+': lambda x, y: x + y, '-': lambda x, y: x - y, '*': lambda x, y: x * y,
                            '/': lambda x, y: x / y, '%': lambda x, y: x % y, '<': lambda x, y: x < y,
                            '<=': lambda x, y: x <= y, '>': lambda x, y: x > y, '>=': lambda x, y: x >= y,
                            '==': lambda x, y: x == y, '!=': lambda x, y: x != y, '||': lambda x, y: x or y,
                            '&&': lambda x, y: x and y, '|': lambda x, y: x | y, '^': lambda x, y: x ^ y,
                            '&': lambda x, y: x & y, '<<': lambda x, y: x << y, '>>': lambda x, y: x >> y}

    def __call__(self, op, arg1, arg2):
        return self.expressions[op](arg1, arg2)
