import os
import sys

import ply.yacc as yacc
from ply.lex import LexError
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
            res = self.parser.parse(t, debug=True)
            return res, self.ok, self._functions
        except LexError:
            sys.stderr.write(f'Illegal token {t}\n')



    def p_program(self, p):
        """program : statements"""
        p[0] = Node('program', children=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_command(self, p):
        """command : CMD DIRECT"""
        p[2] = Node('robot_direction', p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        p[0] = Node('robot_command', p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_statements(self, p):
        """statements : statements statement
                        | statement"""
        if len(p) == 2:
            p[0] = Node('statement', children=p[1])
        else:
            p[0] = Node('statements', children=[p[1], Node('statement', children=p[2])])

    def p_statement(self, p):
        """statement : empty eoe
                      | variable eoe
                      | assignment eoe
                      | from eoe
                      | if eoe
                      | function eoe
                      | function_call eoe
                      | command eoe"""
        p[0] = p[1]

    def p_eoe(self, p):
        """eoe : NEWLINE
               | SEMICOLON
               | SEMICOLON NEWLINE"""
        p[0] = p[1]

    def p_empty(self, p):
        """empty : """
        pass

    def p_assigment(self, p):
        """assignment : variable ASSIGNMENT expression"""
        p[0] = Node('assignment', value=p[2], children=[p[1], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_variable(self, p):
        """variable : NAME LBRACKET index RBRACKET"""
        # if len(p) == 3:
        #     p[0] = Node('variable', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        # else:
            # p[2] = SyntaxTreeNode('bracket', value=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
            # p[4] = SyntaxTreeNode('bracket', value=p[4], lineno=p.lineno(4), lexpos=p.lexpos(4))
        p[0] = Node('variable', value=p[1], children=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))
    def p_var(self,p):
        """var : NAME"""
        p[0] = Node('var', value=p[1])

    def p_index(self, p):
        """index :
                 | index COMMA INT
                 | INT"""
        if len(p) == 1:
            p[0] = Node('null_index', value=0)
        elif len(p) == 4:
            p[3] = Node('index', value=p[3], lineno=p.lineno(3), lexpos=p.lexpos(3))
            p[0] = Node('list_index', children=[p[1], p[3]], lineno=p.lineno(3), lexpos=p.lexpos(3))
        else:
            p[0] = Node('index', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))   #INITIALIZATION

    def p_expression(self, p):
        """expression : variable
                        | var
                        | const
                        | operation
                        | logic_expr
                        | function_call"""
        p[0] = p[1]

    def p_const(self, p):
        """const : INT
                 | FLOAT
                 | BOOL
                 | CELLTYPE"""
        p[0] = Node('const', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_operations(self, p):
        """operation : expression PLUS expression
                    | expression MINUS expression
                    | MINUS expression"""
        if len(p) == 3:
            p[0] = Node('un_operation', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('operation', value=p[2], children=[p[1], p[3]], lineno=p.lineno(2), lexpos=p.lexpos(2))

    def p_from(self, p):
        """from : FROM expression TO expression DO FUNCTION NEWLINE statements END
                | FROM expression TO expression function_call
                | FROM expression TO expression WITH STEP expression DO FUNCTION NEWLINE statements END
                | FROM expression TO expression WITH STEP expression function_call"""
        if len(p) == 10:
            p[0] = Node('from_cycle', children={'from': p[2], 'to': p[4], 'body': p[8]},
                                  lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 6:
            p[0] = Node('from_cycle', children={'from': p[2], 'to': p[4], 'call': p[5]},
                                  lineno=p.lineno(1), lexpos=p.lexpos(1))
        elif len(p) == 13:
            p[0] = Node('from_cycle_ws', children={'from': p[2], 'to': p[4], 'body': p[11], 'with_step': p[7]},
                                  lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('from_cycle_ws', children={'from': p[2], 'to': p[4], 'call': p[8], 'with_step': p[7]},
                                  lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_function_call(self, p):
        """function_call : DO NAME"""
        p[2] = Node('function_name', value=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        p[0] = Node('function_call', value=p[1], children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_if(self, p):
        """if : IF logic_expr function_call
              | IF logic_expr DO FUNCTION NEWLINE statements END"""
        if len(p) == 4:
            p[0] = Node('if', p[1], children=[p[2], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('if', p[1], children=[p[2], p[6]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_logic_expr(self, p):
        """logic_expr : expression AND expression
                      | expression OR expression
                      | expression CMP expression"""
        p[0] = Node('logic_expr', p[2], children=[p[1], p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

    def p_function(self, p):
        """function : FUNCTION NAME NEWLINE statements END"""
        p[0] = Node('function', str(p[2]), children={'body': p[4]}, lineno=p.lineno(1),
                              lexpos=p.lexpos(1))
        self._functions[p[2]] = p[0]

        #SYNTAX ERRORS
    def p_assignment_error(self, p):
        """assignment : variable ASSIGNMENT error"""
        p[0] = Node('assign_error', value="Wrong assign", children=p[1], lineno=p.lineno(1),
                              lexpos=p.lexpos(1))
        sys.stderr.write(f'>>> Wrong from\n')

    def p_from_error(self, p):
        """from : FROM expression TO expression WITH STEP expression DO FUNCTION error statements END
                | FROM expression TO expression DO FUNCTION error statements END
                | FROM expression error expression WITH STEP expression DO FUNCTION NEWLINE statements END
                | FROM expression error expression DO FUNCTION NEWLINE statements END
                | FROM expression TO  expression WITH STEP expression DO error NEWLINE statements END
                | FROM expression TO expression DO error NEWLINE statements END
                | FROM expression TO expression error FUNCTION NEWLINE statements END
                | FROM expression TO expression WITH STEP expression error FUNCTION NEWLINE statements END"""
        if len(p) == 10:
            p[0] = Node('error', value="Wrong from", children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('error', value="Wrong from", children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'>>> Wrong from\n')

    def p_if_error(self, p):
        """if : IF logic_expr DO FUNCTION error statements END
              | IF logic_expr DO error NEWLINE statements END
              | IF error DO FUNCTION NEWLINE statements END
              | IF error function_call
              | IF logic_expr error FUNCTION NEWLINE statements END"""
        if len(p) == 4:
            p[0] = Node('error', value="Wrong if", children=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))
        else:
            p[0] = Node('error', value="Wrong if", children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'>>> Wrong if\n')

    def p_function_error(self, p):
        """function : FUNCTION NAME error statements END
                    | error NAME NEWLINE statements END"""
        p[2] = Node('error_func', p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        p[0] = Node('error', value="Wrong function", children=p[2], lineno=p.lineno(1), lexpos=p.lexpos(1))
        sys.stderr.write(f'>>> Wrong function\n')

    def p_error(self, p):
        try:
            sys.stderr.write(f'Syntax error at {p.lineno} line\n')
        except Exception:
            sys.stderr.write(f'SYNTAX error\n')
        self.ok = False


data = ''' function main
m <= true / false;
d <= -m;
d <= 2 in n;
end;'''


# parser = Parser()
# tree, ok, functions = parser.parse(data)
# tree.print()
# print(ok)
# functions['function'].children['body'].print()
