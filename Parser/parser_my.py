import ply.yacc as yacc
from ply.lex import LexError
import sys
from typing import List, Dict, Tuple, Any
sys.path.insert(0, '../')
from Lexer.lexer_my import Lexer
sys.path.insert(0, '../SyntaxTree')
from SyntaxTree import Node

class Parser(object):
    tokens = Lexer.tokens

    def __init__(self):
        self.ok = True
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)
        self._functions = dict()

    def parse(self, t):
        try:
            res = self.parser.parse(t)
            return res, self.ok, self._functions
        except LexError:
            sys.stderr.write(f'Illegal token {t}\n')

    def p_program(self, p):
        """program : statements"""
        p[0] = Node('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_statements(self, p):
        """statements : statements statement
                        | statement"""
        if len(p) == 2:
            p[0] = Node('statement', children=p[1])
        else:
            p[0] = Node('statements', children=[p[1], Node('statement', children=p[2])])
    def p_statement(self, p):
        """statement : empty NEWLINE
                      | declaration NEWLINE
                      | assignment NEWLINE
                      | from NEWLINE
                      | if NEWLINE
                      | function NEWLINE
                      | function_call NEWLINE
                      | command NEWLINE"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty : """
        pass

    def p_declaration(self, p):
        """declaration : types variable
                        |types variable ASSIGNMENT initialization"""
        if len(p) == 3:
            p[0] = Node('declaration', value='VARIABLE', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else: p[0] = Node('declaration', value='VARIABLE', children=[Node('init', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1)), p[4], Node('init_end')], lineno=p.lineno(1), lexpos=p.lexpos(1))
    def p_types(self, p):
        """types : INT
                |BOOL
                |CELL"""
    def p_variable(self, p):
        """variable : NAME
                    | NAME varsize"""
        if len(p) == 2:
            p[0] = Node('variant', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('variant', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_varsize(self, p):
        """varsize : LBRACKET decimal_expression RBRACKET
                    | LBRACKET decimal_expression COMMA decimal_expression RBRACKET"""
        if len(p) == 4:
            p[0] = Node('varsize', children=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
        else:
            p[0] = Node('varsize', children=[p[2], p[4]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    #INITIALIZATION

    def p_initiallization(self, p):
        """initialization : LBRACE init_lists RBRACE"""
        p[0] = p[2]

    def p_init_lists(self, p):
        """init_lists : init_list"""
    #EXPRESSIONS
    def p_const_expressions(self, p):
        """const_expressions : const_expressions COMMA const_expression
                        | const_expression"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('const_expressions', children=[p[1], p[3]])
    def p_const_expression(self, p):
        """const_expression : const_math_expression
                        | const"""
        p[0] = Node('const_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
    def p_expression(self, p):
        """expression : math_expression
                        | const
                        | variable
                        | function_call"""
        p[0] = Node('expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_bool_expression(self, p):
        """bool_expression : bool_math_expression
                            | bool_const
                            | function_call"""
        p[0] = Node('bool_expression', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    # MATH EXPRESSIONS

    def p_math_expression(self, p):
        """math_expression : expression PLUS expression
                            | expression MINUS expression
                            | MINUS expression"""
        if len(p) == 3:
            p[0] = Node('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_const_math_expression(self, p):
        """const_math_expression : const_expression PLUS const_expression
                            | MINUS const_expression"""
        if len(p) == 3:
            p[0] = Node('unar_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('bin_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    #LOGIC EXPRESSION
    def p_logic_expression(self, p):
        """logic_expression : expression AND expression
                            | expression OR expression
                            | MINUS expression"""
        if len(p) == 3:
            p[0] = Node('unar_logic_op', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('bin_logic_op', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    # CONSTANTS

    def p_const(self, p):
        """const : bool_const
                | decimal_const
                | CELL_const"""
        p[0] = p[1]

    def p_decimal_const(self, p):
        """decimal_const : DECIMAL"""
        p[0] = Node('decimal_const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_bool_const(self, p):
        """bool_const : TRUE
                        | FALSE"""
        if p[1] == 'TRUE':
            val = True
        else:
            val = False
        p[0] = Node('bool_const', value=val, lineno=p.lineno(1), lexpos=p.lexpos(1))


    def p_assignment(self, p):
        """assignment : variable ASSIGNMENT expression"""
        p[0] = Node('assignment', value=p[1], children=p[3], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_cmp(self, p):
        """cmp: expression CMP variable
                | variable CMP variable"""
        p[0] = Node('compare', value=p[1], children=p[3],lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_from(self, p):
        """from : FROM expression TO expression DO function
                | FROM expression TO expression WITH STEP expression DO function"""
        p[0] = Node('from', children={'condition': p[2], 'body': p[4]}, lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_if(self, p):
        """if : IF logic_expression function_call"""

    def p_function(self, p):
        """"""

    def p_return(self, p):
        """return : RETURN expression"""
        p[0] = Node('return', children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    #SYNTAX ERRORS
    def p_decl_error(self, p):
        """declaration : VARIANT error
                        | VARIANT variant ASSIGNMENT error
                        | declaration error"""
        if len(p) == 3:
            p[0] = Node('error', value='Declaration error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant declaration\n')
        else:
            p[0] = Node('error', value='Initialization error', lineno=p.lineno(2), lexpos=p.lexpos(2))
            sys.stderr.write(f'==> Error in variant initialization\n')