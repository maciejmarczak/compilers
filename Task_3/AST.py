class Node(object):
    #def __str__(self):
    #    return self.printTree()
    pass

class ProgramParts(Node):
    def __init__(self):
        self.children = []

    def appendPart(self, part):
        self.children.append(part)


class Const(Node):
    def __init__(self, line, value):
        self.value = value
        self.line = line


class Integer(Const):
    def __init__(self, line, value):
        Const.__init__(self, line, value)


class Float(Const):
    def __init__(self, line, value):
        Const.__init__(self, line, value)


class String(Const):
    def __init__(self, line, value):
        Const.__init__(self, line, value)


class Variable(Node):
    def __init__(self, line, name):
        self.name = name
        self.line = line


class BinExpr(Node):
    def __init__(self, line, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        self.line = line


class ExpressionList(Node):
    def __init__(self):
        self.children = []

    def addExpression(self, expr):
        self.children.append(expr)


class GroupedExpression(Node):
    def __init__(self, interior):
        self.interior = interior


class FunctionExpression(Node):
    def __init__(self, retType, name, args, body):
        self.retType = retType
        self.name = name
        self.args = args
        self.body = body


class FunctionExpressionList(Node):
    def __init__(self):
        self.children = []

    def addFunction(self, fundef):
        self.children.append(fundef)


class DeclarationList(Node):
    def __init__(self):
        self.children = []

    def addDeclaration(self, declaration):
        self.children.append(declaration)


class Declaration(Node):
    def __init__(self, type, inits):
        self.type = type
        self.inits = inits


class InvocationExpression(Node):
    def __init__(self, line, name, args):
        self.name = name
        self.args = args
        self.line = line

   
class Argument(Node):
    def __init__(self, line, type, name):
        self.type = type
        self.name = name
        self.line = line


class ArgumentList(Node):
    def __init__(self):
        self.children = []
        
    def addArgument(self, arg):
        self.children.append(arg)


class InitList(Node):
    def __init__(self):
        self.children = []
        
    def addInit(self, init):
        self.children.append(init)


class Init(Node):
    def __init__(self, line, name, expr):
        self.name = name
        self.expr = expr
        self.line = line


class InstructionList(Node):
    def __init__(self):
        self.children = []
    
    def addInstruction(self, instr):
        self.children.append(instr)


class PrintInstr(Node):
    def __init__(self, line, expr):
        self.expr = expr
        self.line = line


class LabeledInstr(Node):
    def __init__(self, id, instr):
        self.id = id
        self.instr = instr


class AssignmentInstr(Node):
    def __init__(self, line, id, expr):
        self.id = id
        self.expr = expr
        self.line = line


class CompoundInstr(Node):
    def __init__(self, declarations, instructions):
        self.declarations = declarations
        self.instructions = instructions


class ChoiceInstr(Node):
    def __init__(self, condition, action, alternateAction=None):
        self.condition = condition
        self.action = action
        self.alternateAction = alternateAction


class WhileInstr(Node):
    def __init__(self, condition, instruction):
        self.condition = condition
        self.instruction = instruction


class RepeatInstr(Node):
    def __init__(self, instructions, condition):
        self.instructions = instructions
        self.condition = condition


class ReturnInstr(Node):
    def __init__(self, line, expression):
        self.expression = expression
        self.line = line


class BreakInstr(Node):
    pass


class ContinueInstr(Node):
    pass


class Program(Node):
    def __init__(self, declarations, fundefs, instructions):
        self.declarations = declarations
        self.fundefs = fundefs
        self.instructions = instructions
