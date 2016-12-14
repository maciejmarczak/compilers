#!/usr/bin/python

import AST
from SymbolTable import SymbolTable, FunctionSymbol, VariableSymbol
from Ttype import ScopeType, Types, Ttype


class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)


class TypeChecker(NodeVisitor):

    def __init__(self):
        self.ttype = Ttype()
        self.symbol_table = SymbolTable()

    def visit_Program(self, node):
        self.symbol_table.push_scope(ScopeType.GLOBAL)
        self.visit(node.sections)
        self.symbol_table.pop_scope()

    def visit_Declaration(self, node):
        self.symbol_table.current_scope.current_type = node.type_name
        self.visit(node.inits)
        self.symbol_table.current_scope.current_type = None

    def visit_Init(self, node):
        expr_type = self.visit(node.expression)
        declr_type = self.symbol_table.current_scope.current_type
        definition = self.symbol_table.current_scope.find(node.identifier)
        if definition is not None and isinstance(definition, FunctionSymbol):
            message = "Function identifier '{}' used as a variable".format(node.identifier)
            self.log_error(message, node.lineno)
        elif self.symbol_table.current_scope.get(node.identifier) is not None:
            message = "Variable '{}' already declared".format(node.identifier)
            self.log_error(message, node.lineno)
        elif not self.ttype.get_type('=', declr_type, expr_type):
            message = "Assignment of {} to {}".format(expr_type, declr_type)
            self.log_error(message, node.lineno)
        else:
            self.check_precision_loss(declr_type, expr_type, node.lineno)
            self.symbol_table.current_scope.put(node.identifier, VariableSymbol(node.identifier, declr_type))

    def visit_PrintInstr(self, node):
        self.visit(node.expressions)

    def visit_LabeledInstr(self, node):
        if self.symbol_table.has_label(node.identifier):
            message = "Label '{}' already in use".format(node.identifier)
            self.log_error(message, node.lineno)
        else:
            self.symbol_table.put_label(node.identifier)
        self.visit(node.instr)

    def visit_Assignment(self, node):
        expr_type = self.visit(node.expression)
        var_def = self.symbol_table.current_scope.find(node.identifier)
        if var_def is None:
            message = "Variable '{}' undefined in current scope".format(node.identifier)
            self.log_error(message, node.lineno)
        elif not self.ttype.get_type('=', var_def.type, expr_type) and expr_type:
            message = "Assignment of {} to {}".format(expr_type, var_def.type)
            self.log_error(message, node.lineno)
        elif expr_type:
            self.check_precision_loss(var_def.type, expr_type, node.lineno)

    def visit_ChoiceInstr(self, node):
        self.visit(node.condition)
        self.visit(node.if_instr)
        if node.else_instr is not None:
            self.visit(node.else_instr)

    def visit_WhileInstr(self, node):
        self.visit(node.condition)
        self.symbol_table.push_scope(ScopeType.LOOP)
        self.visit(node.instr)
        self.symbol_table.pop_scope()

    def visit_RepeatInstr(self, node):
        self.symbol_table.push_scope(ScopeType.LOOP)
        self.visit(node.instrs)
        self.symbol_table.pop_scope()
        self.visit(node.condition)

    def visit_BinExpr(self, node):
        type_left = self.visit(node.left)
        type_right = self.visit(node.right)
        op = node.op
        return_type = self.ttype.get_type(op, type_left, type_right)
        if not return_type:
            message = "Illegal operation, {} {} {}".format(type_left, op, type_right)
            self.log_error(message, node.lineno)
        return return_type

    def visit_ReturnInstr(self, node):
        fun_scope = self.symbol_table.current_scope.find_scope(ScopeType.FUNCTION)
        if fun_scope is None:
            self.log_error('return instruction outside a function', node.lineno)
        else:
            return_type = self.visit(node.expression)
            symbol = self.symbol_table.fun_symbol
            symbol.found_return()
            fun_type = symbol.type
            if return_type:
                if return_type != fun_type:
                    message = "Improper returned type, expected {}, got {}".format(fun_type, return_type)
                    self.log_error(message, node.lineno)

    def loop_instr(self, node):
        if self.symbol_table.current_scope.find_scope(ScopeType.LOOP) is None:
            message = "{} instruction outside a loop".format(node.name)
            self.log_error(message, node.lineno)

    def visit_ContinueInstr(self, node):
        self.loop_instr(node)

    def visit_BreakInstr(self, node):
        self.loop_instr(node)

    def visit_Identifier(self, node):
        id_type = self.symbol_table.current_scope.find(node.identifier)
        if id_type is None:
            message = "Usage of undeclared variable '{}'".format(node.identifier)
            self.log_error(message, node.lineno)
            return None
        if isinstance(id_type, FunctionSymbol):
            message = "Function identifier '{}' used as a variable".format(node.identifier)
            self.log_error(message, node.lineno)
        return id_type.type

    def visit_CompoundInstr(self, node):
        self.symbol_table.push_scope(ScopeType.NESTED)
        self.visit(node.statements)
        self.symbol_table.pop_scope()

    def visit_FunDef(self, node):
        s = self.symbol_table.current_scope
        symbol = s.find(node.name)
        if isinstance(symbol, FunctionSymbol):
            message = "Redefinition of function '{}'".format(node.name)
            self.log_error(message, node.lineno)
        elif isinstance(symbol, VariableSymbol):
            message = "Variable identifier '{}' used as function name".format(node.name)
            self.log_error(message, node.lineno)
        else:
            args_type = [arg.arg_type for arg in node.args]
            fun_symbol = FunctionSymbol(node.name, node.return_type, args_type)
            self.symbol_table.current_scope.put(node.name, fun_symbol)

            self.symbol_table.push_scope(ScopeType.FUNCTION, fun_symbol)
            self.visit(node.args)
            self.visit(node.statements)

            if not fun_symbol.has_return:
                message = "Missing return statement in function '{}' returning {}".format(node.name, node.return_type)
                self.log_error(message, node.end_lineno)

            self.symbol_table.pop_scope()

    def visit_FunArg(self, node):
        if self.symbol_table.current_scope.get(node.arg) is None:
            self.symbol_table.current_scope.put(node.arg, VariableSymbol(node.arg, node.arg_type))
        else:
            message = "Variable '{}' already declared".format(node.arg)
            self.log_error(message, node.lineno)

    def visit_FunCall(self, node):
        fun_def = self.symbol_table.current_scope.find(node.name)
        if fun_def is None or not isinstance(fun_def, FunctionSymbol):
            message = "Call of undefined function '{}'".format(node.name)
            self.log_error(message, node.lineno)
            return None
        if len(node.args) != len(fun_def.args_types):
            message = "Improper number of args in {} call".format(node.name)
            self.log_error(message, node.lineno)
        else:
            expr_types = [self.visit(arg) for arg in node.args]
            for (actual, arg_type) in zip(expr_types, fun_def.args_types):
                if not self.ttype.get_type('=', arg_type, actual):
                    message = "Improper type of args in {} call".format(node.name)
                    self.log_error(message, node.lineno)
                    break  # ???
                else:
                    self.check_precision_loss(arg_type, actual, node.lineno)
        return fun_def.type

    def visit_Integer(self, node):
        return Types.INT

    def visit_Float(self, node):
        return Types.FLOAT

    def visit_String(self, node):
        return Types.STRING

    def check_precision_loss(self, type_left, type_right, lineno):
        if type_left == Types.INT and type_right == Types.FLOAT:
            message = "possible precision loss: assigning {} to {}".format(type_right, type_left)
            self.log_warning(message, lineno)

    def log_error(self, message, lineno):
        print("Error: {}: line {}".format(message, lineno))

    def log_warning(self, message, lineno):
        print("Warning: {}: line {}".format(message, lineno))
