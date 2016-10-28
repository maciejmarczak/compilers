
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
    def printTree(self):
        return ''

    @addToClass(AST.Const)
    def printTree(self, level = 0):
        return printTree(self.val, level)

    @addToClass(AST.Declaration)
    def printTree(self, level = 0):
        return printTree('DECL', level) + printTree(self.inits, level + 1)

    @addToClass(AST.InitList)
    def printTree(self, level = 0):
        return "".join(map(lambda x: printTree(x, level), self.inits))

    @addToClass(AST.Init)
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
