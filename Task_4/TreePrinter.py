import AST


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func

    return decorator


def nextLevel(expression):
    res = ""
    for line in str(expression).split('\n'):
        res += "" if len(line) == 0 else "| " + line + "\n"
    return res


class TreePrinter:
    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.Program)
    def printTree(self):
        res = ""
        for component in self.sections:
            res += str(component)
        return res

    @addToClass(AST.Declaration)
    def printTree(self):
        res = "DECL\n"
        for init in self.inits:
            res += str(init)
        return res

    @addToClass(AST.Init)
    def printTree(self):
        return "| =\n| | " + self.identifier + "\n| | " + str(self.expression) + "\n"

    #instructions
    @addToClass(AST.PrintInstr)
    def printTree(self):
        res = "PRINT\n"
        for expression in self.expressions:
            res += nextLevel(expression)
        return res

    @addToClass(AST.LabeledInstr)
    def printTree(self):
        return "LABEL\n| " + self.identifier + "\n" + nextLevel(self.instr)

    @addToClass(AST.Assignment)
    def printTree(self):
        return "=\n| " + self.identifier + '\n' + nextLevel(self.expression)

    @addToClass(AST.ChoiceInstr)
    def printTree(self):
        res = "IF\n"
        res += nextLevel(self.condition)
        res += nextLevel(self.if_instr)
        if self.else_instr:
            res += "ELSE\n"
            res += nextLevel(self.else_instr)
        return res

    @addToClass(AST.WhileInstr)
    def printTree(self):
        res = "WHILE\n"
        res += nextLevel(self.condition)
        res += nextLevel(self.instr)
        return res

    @addToClass(AST.RepeatInstr)
    def printTree(self):
        res = "REPEAT\n"
        for instr in self.instrs:
            res += nextLevel(instr)
        res += "UNTIL\n"
        res += nextLevel(self.condition)
        return res

    @addToClass(AST.ReturnInstr)
    def printTree(self):
        res = "RETURN\n"
        res += nextLevel(self.expression)
        return res

    @addToClass(AST.CompoundInstr)
    def printTree(self):
        res = ""
        for instr in self.statements:
            res += str(instr) + "\n"
        return res

    @addToClass(AST.FunDef)
    def printTree(self):
        res = "FUNDEF\n| " + self.name + "\n| RET " \
                        + self.return_type + "\n"
        for arg in self.args:
            res += str(arg)
        res2 = ""
        for instr in self.statements:
            res2 += str(instr) + "\n"
        res += nextLevel(res2)
        return res

    @addToClass(AST.FunArg)
    def printTree(self):
        return "| ARG " + self.arg + "\n"

    @addToClass(AST.FunCall)
    def printTree(self):
        res = "FUNCALL\n| " + self.name + "\n"
        for arg in self.args:
            res += nextLevel(arg)
        return res

    @addToClass(AST.Identifier)
    def printTree(self):
        return self.identifier

    @addToClass(AST.BinExpr)
    def printTree(self):
        res = self.op + '\n'
        res += nextLevel(self.left)
        res += nextLevel(self.right)
        return res

    @addToClass(AST.Const)
    def printTree(self):
        return str(self.value)
