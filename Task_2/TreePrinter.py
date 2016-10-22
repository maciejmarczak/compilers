
import AST

PIPE = '| '

def addToClass(cls):

    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.Declaration)
    def printTree(self, level = 0):
        return PIPE * level + str(self.type) + "\n" + self.inits.printTree(level + 1)

    @addToClass(AST.InitList)
    def printTree(self, level = 0):
        return "".join(map(lambda x: x.printTree(level), self.inits))

    @addToClass(AST.Init)
    def printTree(self, level = 0):
        return PIPE * level + str(self.id) + "\n"

    @addToClass(AST.BinExpr)
    def printTree(self):
        pass
        # ...

    # @addToClass ...
    # ...
