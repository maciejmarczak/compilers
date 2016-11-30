from optparse import _parse_int
import AST
import SymbolTable
from Memory import *
from Exceptions import *
from visit import *


class Interpreter(object):
    def __init__(self):
        self.globalMem = MemoryStack()

    @on('node')
    def visit(self, node):
        pass

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.lhs.accept(self)
        r2 = node.rhs.accept(self)
        return eval("a" + node.op + "b", {"a": r1, "b": r2})

    @when(AST.GroupedExpression)
    def visit(self, node):
        return node.interior.accept(self)


    #! mamy specjalizowane wersje
    #@when(AST.Const)
    #def visit(self, node):
    #    return node.value

    @when(AST.WhileInstr)
    def visit(self, node):
        while node.condition.accept(self):
            try:
                node.instruction.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass

    @when(AST.RepeatInstr)
    def visit(self, node):
        while True:
            try:
                node.instructions.accept(self)
                if node.condition.accept(self):
                    break
            except BreakException:
                break
            except ContinueException:
                pass

    @when(AST.ChoiceInstr)
    def visit(self, node):
        if node.condition.accept(self):
            return node.action.accept(self)
        elif node.alternateAction:
            return node.alternateAction.accept(self)
        else:
            pass

    @when(AST.ExpressionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)



    @when(AST.InstructionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.FunctionExpressionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.CompoundInstr)
    def visit(self, node):
        node.declarations.accept(self)
        node.instructions.accept(self)



    @when(AST.FunctionExpression)
    def visit(self, node):
        self.globalMem.peek().put(node.name, node)



    @when(AST.InvocationExpression)
    def visit(self, node):
        fun = self.globalMem.get(node.name)#EXCEPTION
        functionMem = Memory(node.name)
        for argExpr, actualArg in zip(node.args.children, fun.args.children):
            functionMem.put(actualArg.accept(self), argExpr.accept(self))
        self.globalMem.push(functionMem)
        try:
            fun.body.accept(self)
        except ReturnValueException as e:
            return e.value
        finally:
            self.globalMem.pop()

    @when(AST.Argument)
    def visit(self, node):
        return node.name


    @when(AST.ArgumentList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.AssignmentInstr)
    def visit(self, node):
        expr_accept = node.expr.accept(self)
        self.globalMem.set(node.id, expr_accept)
        return expr_accept


    @when(AST.LoopControlInstr)
    def visit(self, node):
        if node.type == 'Break':
            raise BreakException()
        elif node.type == 'Continue':
            raise ContinueException()

    @when(AST.Declaration)
    def visit(self, node):
        node.inits.accept(self)


    @when(AST.DeclarationList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.ExpressionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.Float)
    def visit(self, node):
        return float(node.value)


    @when(AST.Init)
    def visit(self, node):
        expr_accept = node.expr.accept(self)
        self.globalMem.peek().put(node.name, expr_accept)
        return expr_accept


    @when(AST.InitList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)


    @when(AST.Integer)
    def visit(self, node):
        return int(node.value);

    @when(AST.LabeledInstr)
    def visit(self, node):
        pass


    @when(AST.PrintInstr)
    def visit(self, node):
        print node.expr.accept(self)


    @when(AST.ProgramParts)
    def visit(self, node):
        for p in node.children:
            p.accept(self)


    @when(AST.ReturnInstr)
    def visit(self, node):
        value = node.expression.accept(self)
        raise ReturnValueException(value)


    @when(AST.String)
    def visit(self, node):
        return node.value


    @when(AST.Variable)
    def visit(self, node):
        return self.globalMem.get(node.name)




