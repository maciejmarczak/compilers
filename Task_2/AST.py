class Node(object):
    def __str__(self):
        return self.printTree()


class Epsilon(Node):
    pass


class File(Node):
    def __init__(self, program):
        self.program = program


class Program(Node):
    def __init__(self, declarations, instructions_opt, fundefs_opt):
        self.declarations = declarations
        self.instructions_opt = instructions_opt
        self.fundefs_opt = fundefs_opt


class Declarations(Node):
    def __init__(self):
        self.declarations = []

    def appendDeclaration(self, declaration):
        self.declarations.append(declaration)


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


class BinExpr(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class FunCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args


class Assignment(Node):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr


class Instructions_OPT(Node):
    def __init__(self, instructions):
        self.instructions = instructions


class Instructions(Node):
    def __init__(self):
        self.instructions = []

    def appendInstruction(self, instruction):
        self.instructions.append(instruction)


class PrintInstruction(Node):
    def __init__(self, expressions):
        self.expressions = expressions


class LabeledInstruction(Node):
    def __init__(self, id, instruction):
        self.id = id
        self.instruction = instruction


class ChoiceInstruction(Node):
    def __init__(self, condition, instruction, elseInstruction = None):
        self.condition = condition
        self.instruction = instruction
        self.elseInstruction = elseInstruction


class WhileLoop(Node):
    def __init__(self, condition, instruction):
        self.condition = condition
        self.instruction = instruction


class RepeatInstruction(Node):
    def __init__(self, instructions, condition):
        self.instructions = instructions
        self.condition = condition


class ReturnInstruction(Node):
    def __init__(self, expression):
        self.expression = expression


class ContinueInstruction(Node):
    pass


class BreakInstruction(Node):
    pass


class CompoundInstruction(Node):
    def __init__(self, declarations, instructions_opt):
        self.declarations = declarations
        self.instructions_opt = instructions_opt


class Condition(Node):
    def __init__(self, expression):
        self.expression = expression


class Fundefs(Node):
    def __init__(self):
        self.fundefs = []

    def appendFundef(self, fundef):
        self.fundefs.append(fundef)


class Fundef(Node):
    def __init__(self, ret, name, args, compound):
        self.ret = ret
        self.name = name
        self.args = args
        self.compound = compound


class ArgsList(Node):
    def __init__(self):
        self.args = []

    def appendArg(self, arg):
        self.args.append(arg)


class Arg(Node):
    def __init__(self, type, id):
        self.type = type
        self.id = id


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
