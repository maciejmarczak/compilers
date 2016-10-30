
import AST

PIPE = '| '

def addToClass(cls):

    def decorator(func):
        setattr(cls, func.__name__,func)
        return func
    return decorator


def printTree(element, level):
    cname = element.__class__.__name__
    if cname == "str" or cname == "int" or cname == "float":
        return PIPE * level + str(element) + "\n"
    else:
        return element.printTree(level)

class TreePrinter:
    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.Epsilon)
    def printTree(self, level = 0):
        return ''

    @addToClass(AST.Const)
    def printTree(self, level = 0):
        return printTree(self.val, level)

    @addToClass(AST.File)
    def printTree(self, level = 0):
        return printTree(self.program, level)

    @addToClass(AST.Program)
    def printTree(self, level = 0):
        return printTree(self.head, level) + printTree(self.tail, level)

    @addToClass(AST.Declarations)
    def printTree(self, level = 0):
        return "".join(map(lambda x: printTree(x, level), self.declarations))

    @addToClass(AST.Declaration)
    def printTree(self, level = 0):
        return printTree('DECL', level) + printTree(self.inits, level + 1)

    @addToClass(AST.InitList)
    def printTree(self, level = 0):
        return "".join(map(lambda x: printTree(x, level), self.inits))

    @addToClass(AST.Init)
    def printTree(self, level = 0):
        return printTree('=', level) + printTree(self.id, level + 1) + printTree(self.expr, level + 1)

    @addToClass(AST.Instructions_OPT)
    def printTree(self, level = 0):
        return printTree(self.instructions, level)

    @addToClass(AST.Instructions)
    def printTree(self, level = 0):
        return "".join(map(lambda x: printTree(x, level), self.instructions))

    @addToClass(AST.PrintInstruction)
    def printTree(self, level = 0):
        return printTree('PRINT', level) + printTree(self.expressions, level + 1)

    @addToClass(AST.LabeledInstruction)
    def printTree(self, level = 0):
        return printTree(self.id, level) + printTree(self.instruction, level + 1)

    @addToClass(AST.ChoiceInstruction)
    def printTree(self, level = 0):
        return printTree('IF', level) + printTree(self.condition, level + 1) + printTree(self.instruction, level + 1) + ( ( printTree('ELSE', level) +  printTree(self.elseInstruction, level + 1) ) if self.elseInstruction is not None else "" )

    @addToClass(AST.WhileLoop)
    def printTree(self, level = 0):
        return printTree('WHILE', level) + printTree(self.condition, level + 1) + printTree(self.instruction, level + 1)

    @addToClass(AST.RepeatInstruction)
    def printTree(self, level = 0):
        return printTree('REPEAT', level) + printTree(self.instructions, level + 1) + printTree('UNTIL', level) + printTree(self.condition, level + 1)

    @addToClass(AST.ReturnInstruction)
    def printTree(self, level = 0):
        return printTree('RETURN', level) + printTree(self.expression, level + 1)

    @addToClass(AST.ContinueInstruction)
    def printTree(self, level = 0):
        return printTree('CONTINUE', level)

    @addToClass(AST.BreakInstruction)
    def printTree(self, level = 0):
        return printTree('BREAK', level)

    @addToClass(AST.CompoundInstruction)
    def printTree(self, level = 0):
        return printTree('COMPOUND', level) + printTree(self.declarations, level + 1) + printTree(self.instructions_opt, level + 1)

    @addToClass(AST.Condition)
    def printTree(self, level = 0):
        return printTree(self.expression, level)

    @addToClass(AST.Assignment)
    def printTree(self, level = 0):
        return printTree('=', level) + printTree(self.id, level + 1) + printTree(self.expr, level + 1)

    @addToClass(AST.BinExpr)
    def printTree(self, level = 0):
        return printTree(self.op, level) + printTree(self.left, level + 1) + printTree(self.right, level + 1)

    @addToClass(AST.ExprList)
    def printTree(self, level = 0):
        return "".join(map(lambda x: printTree(x, level), self.exprs))

    @addToClass(AST.FunCall)
    def printTree(self, level = 0):
        return printTree('FUNCALL', level) + printTree(self.name, level + 1) + printTree(self.args, level + 1)
