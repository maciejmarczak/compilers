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
            print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')".format(p.lineno,
                                                                                      self.scanner.find_tok_column(p),
                                                                                      p.type, p.value))
        else:
            print("Unexpected end of input")

    def p_program(self, p):
        """program : sections"""
        p[0] = AST.Program(p[1])

    def p_sections(self, p):
        """sections : sections section
                      | """
        p[0] = [] if len(p) == 1 else p[1] + [p[2]]

    def p_section(self, p):
        """section    : fundef
                        | statement """
        p[0] = p[1]

    def p_statement(self, p):
        """statement    : declaration
                        | instruction """
        p[0] = p[1]

    def p_statements(self, p):
        """statements : statements statement
                    | statement"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_declaration(self, p):
        """declaration : TYPE inits ';' 
                       | error ';' """
        p[0] = p[1] if len(p) == 3 else AST.Declaration(p[1], p[2])

    def p_inits(self, p):
        """inits : inits ',' init
                 | init """
        p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]

    def p_init(self, p):
        """init : ID '=' expression """
        p[0] = AST.Init(p[1], p[3], p.lineno(1))

    def p_instructions(self, p):
        """instructions : instructions instruction
                        | instruction """
        p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

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
        p[0] = AST.PrintInstr(p[2])

    def p_labeled_instr(self, p):
        """labeled_instr : ID ':' instruction """
        p[0] = AST.LabeledInstr(p[1], p[3], p.lineno(1))

    def p_assignment(self, p):
        """assignment : ID '=' expression ';' """
        p[0] = AST.Assignment(p[1], p[3], p.lineno(1))

    def p_choice_instr(self, p):
        """choice_instr : IF '(' condition ')' instruction  %prec IFX
                        | IF '(' condition ')' instruction ELSE instruction
                        | IF '(' error ')' instruction  %prec IFX
                        | IF '(' error ')' instruction ELSE instruction """
        p[0] = AST.ChoiceInstr(*p[3::2])

    def p_while_instr(self, p):
        """while_instr : WHILE '(' condition ')' instruction
                       | WHILE '(' error ')' instruction """
        p[0] = AST.WhileInstr(p[3], p[5])

    def p_repeat_instr(self, p):
        """repeat_instr : REPEAT instructions UNTIL condition ';' """
        p[0] = AST.RepeatInstr(p[2], p[4])

    def p_return_instr(self, p):
        """return_instr : RETURN expression ';' """
        p[0] = AST.ReturnInstr(p[2], p.lineno(1))

    def p_continue_instr(self, p):
        """continue_instr : CONTINUE ';' """
        p[0] = AST.ContinueInstr(p.lineno(1))

    def p_break_instr(self, p):
        """break_instr : BREAK ';' """
        p[0] = AST.BreakInstr(p.lineno(1))

    def p_compound_instr(self, p):
        """compound_instr : '{' statements '}' """
        p[0] = AST.CompoundInstr(p[2])

    def p_condition(self, p):
        """condition : expression"""
        p[0] = p[1]

    def p_const(self, p):
        """const : float
                 | integer
                 | string"""
        p[0] = p[1]

    def p_integer(self, p):
        """integer : INTEGER"""
        p[0] = AST.Integer(p[1])


    def p_float(self, p):
        """float : FLOAT"""
        p[0] = AST.Float(p[1])


    def p_string(self, p):
        """string : STRING"""
        p[0] = AST.String(p[1])

    def p_bin_expr(self, p):
        """expression : expression '+' expression
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
                      | expression GE expression"""
        p[0] = AST.BinExpr(p[2], p[1], p[3], p.lineno(2))

    def p_funcall_expr(self, p):
        """expression : ID '(' expr_list_or_empty ')'
                      | ID '(' error ')' """
        p[0] = AST.FunCall(p[1], p[3], p.lineno(1))

    def p_bracket_expr(self, p):
        """ expression : '(' expression ')'
                       | '(' error ')'"""
        p[0] = p[2]

    def p_expression(self, p):
        """expression : const
                      | ID"""
        p[0] = AST.Identifier(p[1], p.lineno(1)) if type(p[1]) is str else p[1]

    def p_expr_list_or_empty(self, p):
        """expr_list_or_empty : expr_list
                              | """
        p[0] = [] if len(p) == 1 else p[1]

    def p_expr_list(self, p):
        """expr_list : expr_list ',' expression
                     | expression """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_fundef(self, p):
        """fundef : TYPE ID '(' args_list_or_empty ')' '{' statements '}' """
        p[0] = AST.FunDef(p[1], p[2], p[4], p[7], p.lineno(1), p.lineno(8))

    def p_args_list_or_empty(self, p):
        """args_list_or_empty : args_list
                              | """
        p[0] = [] if len(p) == 1 else p[1]

    def p_args_list(self, p):
        """args_list : args_list ',' arg 
                     | arg """
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_arg(self, p):
        """arg : TYPE ID """
        p[0] = AST.FunArg(p[1], p[2], p.lineno(1))
