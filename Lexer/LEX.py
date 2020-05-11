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
    'go left': 'GO_LEFT',
    'go right': 'GO_RIGHT',
    'go up': 'GO_UP',
    'go down': 'GO_DOWN',
    'pick left': 'PICK_LEFT',
    'pick right':  'PICK_RIGHT',
    'pick up': 'PICK_UP',
    'pick down': 'PICK_DOWN',
    'drop left': 'DROP_LEFT',
    'drop right':  'DROP_RIGHT',
    'drop up': 'DROP_UP',
    'drop down': 'DROP_DOWN',
    # FUNCTION
    'function': 'FUNCTION',
    'end': 'END',
}


class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=self)

    tokens = ['DECIMAL', 'CELL',
              'ASSIGNMENT', 'PLUS',
              'MINUS', 'AND', 'OR',
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

data = 'from 0 to 10 do go up'
lexer = Lexer()
lexer.input(data)
while True:
    token = lexer.token()
    if token is None:
        break
    else:
        print(token)
