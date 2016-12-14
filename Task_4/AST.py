class Node(object):
    def __str__(self):
        return self.printTree()

    def accept(self, visitor):
        return visitor.visit(self)


# sections : sections section | <empty>
class Program(Node):
    def __init__(self, sections):
        self.sections = sections


class Declaration(Node):
    def __init__(self, type_name, inits):
        self.type_name = type_name
        self.inits = inits


class Init(Node):
    def __init__(self, identifier, expression, lineno):
        self.identifier = identifier
        self.expression = expression
        self.lineno = lineno


# instructions
class PrintInstr(Node):
    def __init__(self, expressions):
        self.expressions = expressions


class LabeledInstr(Node):
    def __init__(self, identifier, instr, lineno):
        self.identifier = identifier
        self.instr = instr
        self.lineno = lineno


class Assignment(Node):
    def __init__(self, identifier, expression, lineno):
        self.identifier = identifier
        self.expression = expression
        self.lineno = lineno


class ChoiceInstr(Node):
    def __init__(self, condition, if_instr, else_instr=None):
        self.condition = condition
        self.if_instr = if_instr
        self.else_instr = else_instr


class WhileInstr(Node):
    def __init__(self, condition, instr):
        self.condition = condition
        self.instr = instr


class RepeatInstr(Node):
    def __init__(self, instrs, condition):
        self.condition = condition
        self.instrs = instrs


class ReturnInstr(Node):
    def __init__(self, expression, lineno):
        self.expression = expression
        self.lineno = lineno


class ContinueInstr(Node):
    def __init__(self, lineno):
        self.name = 'continue'
        self.lineno = lineno


class BreakInstr(Node):
    def __init__(self, lineno):
        self.name = 'break'
        self.lineno = lineno


# compound_instr : '{' statements '}' from new grammar
class CompoundInstr(Node):
    def __init__(self, statements):
        self.statements = statements


# fundef and expressions
class FunDef(Node):
    def __init__(self, return_type, name, args, statements, lineno, end_lineno):
        self.return_type = return_type
        self.name = name
        self.args = args
        self.statements = statements
        self.lineno = lineno
        self.end_lineno = end_lineno


class FunArg(Node):
    def __init__(self, arg_type, arg, lineno):
        self.arg_type = arg_type
        self.arg = arg
        self.lineno = lineno


# expression : ID '(' expr_list_or_empty ')'
class FunCall(Node):
    def __init__(self, name, args, lineno):
        self.name = name
        self.args = args
        self.lineno = lineno


class Identifier(Node):
    def __init__(self, identifier, lineno):
        self.identifier = identifier
        self.lineno = lineno


class BinExpr(Node):
    def __init__(self, op, left, right, lineno):
        self.op = op
        self.left = left
        self.right = right
        self.lineno = lineno


# Consts
class Const(Node):
    def __init__(self, value):
        self.value = value


class Integer(Const):
    def __init__(self, value):
        super(Integer, self).__init__(value)


class Float(Const):
    def __init__(self, value):
        super(Float, self).__init__(value)


class String(Const):
    def __init__(self, value):
        super(String, self).__init__(value)
