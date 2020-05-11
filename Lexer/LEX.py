import sys
import ply.lex as lex

reserved = {
    'bool': 'BOOL',
    'true': 'TRUE',
    'false': 'FALSE',
    'int': 'INT',
    'CELL': 'CELL',
    'EMPTY': 'EMPTY',
    'WALL': 'WALL',
    'BOX': 'BOX',
    'EXIT': 'EXIT',
    'UNDEF': 'UNDEF',
    # INCLUDE
    'in': 'IN',
    'all': 'ALL',
    'some': 'SOME',
    'less': 'LESS',
    # CYCLE
    'from': 'FROM',
    'to': 'TO',
    'with': 'WITH',
    'step': 'STEP',
    'do': 'DO',
    # IF
    'if': 'IF',
    # ROBOT
    'go': 'GO',
    'left': 'LEFT',
    'right': 'RIGHT',
    'up': 'UP',
    'down': 'DOWN',
    'pick': 'PICK',
    'drop': 'DROP',
    # FUNCTION
    'function': 'FUNCTION',
    'end': 'END',
}


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['DECIMAL',
              'ASSIGNMENT', 'PLUS',
              'MINUS', 'AND', 'OR', 'NAME',
              'LBRACKET', 'RBRACKET',
              'NEWLINE', 'SEMICOLON',
              'COMMA'] + list(reserved.values())

    t_ASSIGNMENT = r'\<='
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_AND = r'\&'
    t_OR = r'\|'
    t_COMMA = r'\,'
    t_LBRACKET = r'\('
    t_RBRACKET = r'\)'
    t_SEMICOLON = r'\;'
    t_ignore = ' '

    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'NAME')
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t):
        sys.stderr.write(f'Illegal character: {t.value[0]} at line {t.lexer.lineno}\n')
        t.lexer.skip(1)

    def input(self, data):
        return self.lexer.input(data)

    def token(self):
        return self.lexer.token()


data = 'int a <= 10;' \
       'from a to 20 with step 1 do function ' \
       'a <= a + 1;' \
       'go up and pick left & drop right;' \
       'end;' \
       'if a less 20 do function go down end;' \
       '- some in all in  some less all less false bool EMPTY WALL BOX EXIT UNDEF CELL | drop '
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)
