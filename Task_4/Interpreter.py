import sys

import AST
from Eval import *
from Exceptions import *
from Memory import *
from Ttype import Types
from visit import *

sys.setrecursionlimit(10000)

class Interpreter(object):
    def __init__(self):
        self.global_memory = Memory(GLOBAL_MEM)
        self.memory_stack = MemoryStack(self.global_memory)
        self.declared_type = None
        self.eval = Eval()

    @on("node")
    def visit(self, node):
        pass

    # ====== TYPES ======

    @when(AST.Integer)
    def visit(self, node):
        return int(node.value)

    @when(AST.Float)
    def visit(self, node):
        return float(node.value)

    @when(AST.String)
    def visit(self, node):
        return str(node.value).strip('"')

    # returns value casted according to passed type_str
    def cast(self, type_str, val):
        if type_str == Types.INT:
            return int(val)
        elif type_str == Types.FLOAT:
            return float(val)
        else:
            return str(val)

    # ====== END TYPES ======

    # ====== INSTRUCTIONS ======

    @when(AST.PrintInstr)
    def visit(self, node):
        for expression in node.expressions:
            print(expression.accept(self))

    @when(AST.LabeledInstr)
    def visit(self, node):
        node.instr.accept(self)

    @when(AST.ChoiceInstr)
    def visit(self, node):
        if node.condition.accept(self):
            node.if_instr.accept(self)
        elif node.else_instr is not None:
            node.else_instr.accept(self)

    @when(AST.WhileInstr)
    def visit(self, node):
        while node.condition.accept(self):
            try:
                node.instr.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break

    @when(AST.RepeatInstr)
    def visit(self, node):
        self.memory_stack.push(Memory(COMPOUND_MEM))
        first_exec = True
        while not node.condition.accept(self) or first_exec:
            first_exec = False
            try:
                for instruction in node.instrs:
                    instruction.accept(self)
            except ContinueException:
                continue
            except BreakException:
                break
            except ReturnValueException as e:
                self.memory_stack.pop()
                raise e

        self.memory_stack.pop()

    @when(AST.ReturnInstr)
    def visit(self, node):
        raise ReturnValueException(node.expression.accept(self))

    @when(AST.ContinueInstr)
    def visit(self, node):
        raise ContinueException()

    @when(AST.BreakInstr)
    def visit(self, node):
        raise BreakException()

    @when(AST.CompoundInstr)
    def visit(self, node):
        self.memory_stack.push(Memory(COMPOUND_MEM))
        for statement in node.statements:
            try:
                statement.accept(self)
            except (BreakException, ContinueException, ReturnValueException) as e:
                self.memory_stack.pop()
                raise e

        self.memory_stack.pop()

    # ====== END INSTRUCTIONS ======

    # ====== PROGRAM ROOT ======

    @when(AST.Program)
    def visit(self, node):
        for section in node.sections:
            section.accept(self)

    # ===== END PROGRAM ROOT =====

    # ===== DECLARATIONS & INITS =====

    @when(AST.Declaration)
    def visit(self, node):
        self.declared_type = node.type_name
        for init in node.inits:
            init.accept(self)

    @when(AST.Init)
    def visit(self, node):
        expression_value = node.expression.accept(self)
        if self.declared_type == Types.INT:
            expression_value = int(expression_value)
        elif self.declared_type == Types.FLOAT:
            expression_value = float(expression_value)

        self.memory_stack.insert(node.identifier, expression_value)
        return expression_value

    @when(AST.Assignment)
    def visit(self, node):
        variable_name = node.identifier
        expression_value = node.expression.accept(self)
        expression_value = type(self.memory_stack.get(variable_name))(expression_value)
        self.memory_stack.set(variable_name, expression_value)
        return expression_value

    @when(AST.Identifier)
    def visit(self, node):
        return self.memory_stack.get(node.identifier)

    # ===== END DECLARATIONS & INITS =====

    # ===== FUNCTIONS =====

    @when(AST.FunDef)
    def visit(self, node):
        self.global_memory.put(node.name, node)

    @when(AST.FunArg)
    def visit(self, node):
        return {'arg_name': node.arg, 'arg_type': node.arg_type}

    @when(AST.FunCall)
    def visit(self, node):
        new_memory = Memory(FUN_MEM)
        function_definition = self.global_memory.get(node.name)

        for i in range(0, len(node.args)):
            accepted_def_arg = function_definition.args[i].accept(self)
            accepted_call_arg = node.args[i].accept(self)
            arg_type = accepted_def_arg['arg_type']
            name = accepted_def_arg['arg_name']
            new_memory.put(name, self.cast(arg_type, accepted_call_arg))

        self.memory_stack.push(new_memory)

        try:
            for statement in function_definition.statements:
                statement.accept(self)
        except ReturnValueException as e:
            self.memory_stack.pop()
            return self.cast(function_definition.return_type, e.value)

        self.memory_stack.pop()

    # ===== END FUNCTIONS =====

    @when(AST.BinExpr)
    def visit(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.op == '/' and isinstance(left, int) and isinstance(right, int):
            return left // right
        return self.eval(node.op, left, right)
