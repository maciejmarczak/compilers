#!/usr/bin/python

from scanner import Scanner
import AST



class Cparser(object):


    def __init__(self):
        self.scanner = Scanner()
        self.scanner.build()

    tokens = Scanner.tokens


    precedence = (
       ("nonassoc", 'IFX'),
       ("nonassoc", 'ELSE'),
       ("right", '='),
       ("left", 'OR'),
       ("left", 'AND'),
       ("left", '|'),
       ("left", '^'),
       ("left", '&'),
       ("nonassoc", '<', '>', 'EQ', 'NEQ', 'LE', 'GE'),
       ("left", 'SHL', 'SHR'),
       ("left", '+', '-'),
       ("left", '*', '/', '%'),
    )


    def p_error(self, p):
        if p:
            print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')".format(p.lineno, self.scanner.find_tok_column(p), p.type, p.value))
        else:
            print("Unexpected end of input")


    def p_file(self, p):
        """file : program"""
        program = p[1]
        print AST.File(program)


    def p_program(self, p):
        """program : program_parts"""
        p[0] = p[1]

    def p_program_parts(self, p):
        """program_parts : program_parts program_part
                        | program_part"""
        if len(p) == 3:
            p[0] = p[1]
            p[0].appendPart(p[2])
        else:
            p[0] = AST.ProgramParts()
            p[0].appendPart(p[1])


    def p_program_part(self, p):
        """program_part : declaration
                        | instruction
                        | fundef"""
        p[0] = p[1]


    def p_declaration(self, p):
        """declaration : TYPE inits ';'
                       | error ';' """
        type = p[1]
        inits = p[2]
        p[0] = AST.Declaration(type, inits)


    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        if len(p) == 4:
            p[0] = p[1]
            p[0].addInit(p[3])
        else:
            p[0] = AST.InitList()
            p[0].addInit(p[1])


    def p_init(self, p):
        """init : ID '=' expression """
        id = p[1]
        expression = p[3]
        p[0] = AST.Init(id, expression)


    def p_instruction(self, p):
        """instruction : print_instr
                       | labeled_instr
                       | assignment
                       | choice_instr
                       | while_instr
                       | repeat_instr
                       | return_instr
                       | break_instr
                       | continue_instr
                       | compound_instr
                       | expression ';' """
        p[0] = p[1]


    def p_print_instr(self, p):
        """print_instr : PRINT expr_list ';'
                       | PRINT error ';' """
        p[0] = AST.PrintInstruction(p[2])


    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = AST.LabeledInstruction(p[1], p[3])


    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        p[0] = AST.Assignment(p[1], p[3])


    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction  %prec IFX
                        | IF '(' error ')' instruction ELSE instruction """
        condition = p[3]
        instruction = p[5]
        elseInstruction = p[7] if len(p) == 8 else None
        p[0] = AST.ChoiceInstruction(condition, instruction, elseInstruction)


    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        condition = p[3]
        instruction = p[5]
        p[0] = AST.WhileLoop(condition, instruction)


    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT program_parts UNTIL condition ';' """
        program_parts = p[2]
        condition = p[4]
        p[0] = AST.RepeatInstruction(program_parts, condition)


    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = AST.ReturnInstruction(p[2])


    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = AST.ContinueInstruction()


    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = AST.BreakInstruction()


    def p_compound_instr(self, p):
        """compound_instr : '{' program_parts '}' """
        program_parts = p[2]
        p[0] = AST.CompoundInstruction(program_parts)


    def p_condition(self, p):
        """condition : expression"""
        p[0] = AST.Condition(p[1])


    def p_const(self, p):
        """const : INTEGER
                 | FLOAT
                 | STRING"""
        p[0] = AST.Const(p[1])


    def p_expression(self, p):
        """expression : const
                      | ID
                      | expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression '/' expression
                      | expression '%' expression
                      | expression '|' expression
                      | expression '&' expression
                      | expression '^' expression
                      | expression AND expression
                      | expression OR expression
                      | expression SHL expression
                      | expression SHR expression
                      | expression EQ expression
                      | expression NEQ expression
                      | expression '>' expression
                      | expression '<' expression
                      | expression LE expression
                      | expression GE expression
                      | '(' expression ')'
                      | '(' error ')'
                      | ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        lenp = len(p)
        if lenp == 2:
            p[0] = p[1]
        elif lenp == 4:
            if p[1] == '(':
                if p[2] == ')':
                    p[0] = AST.Epsilon
                else:
                    p[0] = p[2]
            else:
                p[0] = AST.BinExpr(p[2], p[1], p[3])
        elif lenp == 5:
            p[0] = AST.FunCall(p[1], p[3])


    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        if len(p) == 1:
            p[0] = AST.Epsilon()
        else:
            p[0] = p[1]



    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        if len(p) == 2:
            p[0] = AST.ExprList()
            p[0].addExpr(p[1])
        else:
            p[0] = p[1]
            p[0].addExpr(p[3])


    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' compound_instr """
        ret = p[1]
        name = p[2]
        args = p[4]
        compound = p[6]
        p[0] = AST.Fundef(ret, name, args, compound)


    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = AST.Epsilon()

    def p_args_list(self, p):
        """args_list : args_list ',' arg
                     | arg """
        if len(p) == 4:
            p[0] = p[1]
            p[0].appendArg(p[3])
        else:
            p[0] = AST.ArgsList()
            p[0].appendArg(p[1])


    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = AST.Arg(p[1], p[2])
