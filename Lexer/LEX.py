import sys
import ply.lex as lex

reserved = {
    # BOOL
    'true': 'TRUE',
    'false': 'FALSE',
    # CELL
    'EMPTY': 'EMPTY',
    'WALL': 'WALL',
    'BOX': 'BOX',
    'EXIT': 'EXIT',
    'UNDEF': 'UNDEF',
    # INCLUDE
    'in': 'IN',
    'all in': 'ALL_IN',
    'some in': 'SOME_IN',
    'less': 'LESS',
    'all less': 'ALL_LESS',
    'some less': 'SOME_LESS',
    # CYCLE
    'from': 'FROM',
    'to': 'TO',
    'with step': 'WITH_STEP',
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

    tokens = ['DECIMAL', 'CELL',
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


data = 'from 0 to 10 do go up true'
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)
