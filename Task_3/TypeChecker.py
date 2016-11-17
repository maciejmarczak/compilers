#!/usr/bin/python
from collections import defaultdict
from AST import *
from SymbolTable import SymbolTable, FunctionSymbol, VariableSymbol

def print_message(content, line, msgType='error'):
    print 'line {}\t({}):\t{}'.format(line, msgType, content)

def typeDiffer(definedType, usedType, line, allowPrecisionLoss = True):
#    if line == 6:
#       print definedType, usedType, line
#        raise Exception('abc')
    if definedType == usedType or definedType == 'float' and usedType == 'int':
        return False
    elif allowPrecisionLoss and definedType == 'int' and usedType == 'float':
        print_message('Expected int, float given. Precision loss is possible', line, 'warning')
        return False
    else:
        return True


validTypes = defaultdict(lambda: None)
for op in ['+', '-', '*', '/', '%', '<', '>', '<<', '>>', '|', '&', '^', '<=', '>=', '==', '!=']:
    validTypes[(op, 'int', 'int')] = 'int'

for op in ['+', '-', '*', '/']:
    validTypes[(op, 'int', 'float')] = 'float'
    validTypes[(op, 'float', 'int')] = 'float'
    validTypes[(op, 'float', 'float')] = 'float'

for op in ['<', '>', '<=', '>=', '==', '!=']:
    validTypes[(op, 'int', 'float')] = 'int'
    validTypes[(op, 'float', 'int')] = 'int'
    validTypes[(op, 'float', 'float')] = 'int'

validTypes[('+', 'string', 'string')] = 'string'
validTypes[('*', 'string', 'int')] = 'string'

for op in ['<', '>', '<=', '>=', '==', '!=']:
    validTypes[(op, 'string', 'string')] = 'int'


class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        #print "node {} has visitor {}".format(str(node), str(visitor))
        return visitor(node)

    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        elif hasattr(node, "children"):
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, Node):
                            self.visit(item)
                elif isinstance(child, Node):
                    self.visit(child)


                    # simpler version of generic_visit, not so general
                    #def generic_visit(self, node):
                    #    for child in node.children:
                    #        self.visit(child)

class TypeChecker(NodeVisitor):
    def __init__(self):
        self.table = SymbolTable(None, "root")
        self.actType = ""

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_Variable(self, node):
        definition = self.table.getGlobal(node.name)
        if definition is None:
            print_message("Undefined symbol {}".format(node.name), node.line)
        else:
            return definition.type

    def visit_BinExpr(self, node):
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        op = node.op
        if validTypes[(op, lhs, rhs)] is None:
            print_message("Invalid expression", node.line)
        return validTypes[(op, lhs, rhs)]

    def visit_AssignmentInstr(self, node):
        definition = self.table.getGlobal(node.id)
        type = self.visit(node.expr)
        if definition is None:
            print_message("Symbol {} is undefined".format(node.id), node.line)
        elif typeDiffer(definition.type, type, node.line):
            print_message("Cannot assign {} to {}".format(type, definition.type), node.line)

    def visit_GroupedExpression(self, node):
        return self.visit(node.interior)

    def visit_FunctionExpression(self, node):
        if self.table.get(node.name):
            print_message("Function {} is already defined".format(node.name), node.line)
        else:
            function = FunctionSymbol(node.name, node.retType, SymbolTable(self.table, node.name))
            self.table.put(node.name, function)
            self.actFunc = function
            self.table = self.actFunc.table
            if node.args is not None:
                self.visit(node.args)
            self.visit(node.body)
            self.table = self.table.getParentScope()
            self.actFunc = None

    def visit_CompoundInstr(self, node):
        innerScope = SymbolTable(self.table, "innerScope")
        self.table = innerScope
        if node.declarations is not None:
            self.visit(node.declarations)
        self.visit(node.instructions)
        self.table = self.table.getParentScope()

    def visit_ArgumentList(self, node):
        for arg in node.children:
            self.visit(arg)
        self.actFunc.extractParams()

    def visit_Argument(self, node):
        if self.table.get(node.name) is not None:
            print_message("Argument {} is already defined".format(node.name), node.line)
        else:
            self.table.put(node.name, VariableSymbol(node.name, node.type))

    def visit_InvocationExpression(self, node):
        funDef = self.table.getGlobal(node.name)
        if funDef is None or not isinstance(funDef, FunctionSymbol):
            print_message("Function {} is undefined".format(node.name), node.line)
        else:
            if node.args is None and funDef.params != []:
                print_message("Function {} expects {} arguments".format(node.name, len(funDef.params)), node.line)
            else:
                types = [self.visit(x) for x in node.args.children]
                expectedTypes = funDef.params
                for current, expected in zip(types, expectedTypes):
                    if typeDiffer(expected, current, node.line):
                        print_message("Type mismatch: expected {}, got {} ".format(expected, current), node.line)
            return funDef.type

    def visit_ChoiceInstr(self, node):
        self.visit(node.condition)
        self.visit(node.action)
        if node.alternateAction is not None:
            self.visit(node.alternateAction)

    def visit_WhileInstr(self, node):
        self.visit(node.condition)
        self.visit(node.instruction)

    def visit_RepeatInstr(self, node):
        self.visit(node.condition)
        self.visit(node.instructions)

    def visit_ReturnInstr(self, node):
        if self.actFunc is None:
            print_message("Return must be placed in function scope", node.line)
        else:
            type = self.visit(node.expression)
            if typeDiffer(type, self.actFunc.type, node.line):
                print_message("Expected {} instead of {} as the type of returned value".format(self.actFunc.type, type), node.line)

    def visit_Init(self, node):
        initType = self.visit(node.expr)
        if not typeDiffer(self.actType, initType, node.line):
            if self.table.get(node.name) is not None:
                print_message("{} is already defined".format(node.name), node.line)
            else:
                self.table.put(node.name, VariableSymbol(node.name, self.actType))
        else:
            print_message("Cannot assign {} to {} ".format(initType, self.actType), node.line)

    def visit_Declaration(self,node):
        self.actType = node.type
        self.visit(node.inits)
        self.actType = ""

    def visit_PrintInstr(self, node):
        self.visit(node.expr)

    def visit_LabeledInstr(self, node):
        self.visit(node.instr)

    def visit_Program(self, node):
        self.visit(node.declarations)
        self.visit(node.fundefs)
        self.visit(node.instructions)

