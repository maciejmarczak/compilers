
class Node(object):
    def __str__(self):
        return self.printTree()

class Epsilon(Node): pass

class BinExpr(Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class Declaration(Node):
    def __init__(self, type, inits):
        self.type = type
        self.inits = inits


class InitList(Node):
    def __init__(self):
        self.inits = []

    def addInit(self, init):
        self.inits.append(init)


class Init(Node):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr

class Const(Node):
    def __init__(self, val):
        self.val = val

class ExprList(Node):
    def __init__(self):
        self.exprs = []

    def addExpr(self, expr):
        self.exprs.append(expr)

class FunCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Integer(Const):
    pass
    #...


class Float(Const):
    pass
    #...


class String(Const):
    pass
    #...


class Variable(Node):
    pass
    #...




# ...
